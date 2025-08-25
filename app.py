from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="flask_user",  
        password="your_secure_password",  
        database="flask_app"
    )
class DummyModel:
    def predict(self, X):
        district = X[0][3]
        if district == 'Dindigul':
            return ['Tomato']
        if district == 'Villupuram':
            return ['Brinjal']
        elif district == 'Erode':
            return ['Onion']
        elif district == 'Coimbatore':
            return ['Cabbage']
        elif district == 'Kodaikanal':
            return ['Carrot']
        elif district == 'Tirunelveli':
            return ['Banana']
        elif district == 'Salem':
            return ['Mango']
        elif district == 'Kanyakumari':
            return ['Papaya']
        elif district == 'Vellore':
            return ['Guava']
        elif district == 'Tiruvannamalai':
            return ['Pineapple']
        elif district == 'Krishnagiri':
            return ['Potato']
        elif district == 'Thanjavur':
            return ['Rice']
        elif district == 'Kanchipuram':
            return ['Green Chilies']
        elif district == 'Nilgiri':
            return ['Tea']
        else:
            return ['no perdiction']
model = DummyModel()
@app.route('/sign', methods=['GET', 'POST'])
def sign():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        if user and check_password_hash(user['password'], password):
            session['username'] = username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password!', 'danger')
    return render_template('sign.html')
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if 'username' in session:
        return redirect(url_for('index'))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        phone_number = request.form['phone_number']
        aadhar_number = request.form['aadhar_number']
        address = request.form['address']
        hashed_password = generate_password_hash(password)
        db = get_db_connection()
        cursor = db.cursor()
        try:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                flash('Username already exists. Choose another one.', 'warning')
            else:
                cursor.execute(
                    "INSERT INTO users (username, password, phone_number, aadhar_number, address) VALUES (%s, %s, %s, %s, %s)", 
                    (username, hashed_password, phone_number, aadhar_number, address)
                )
                db.commit()
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('sign'))
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", 'danger')
        finally:
            cursor.close()
            db.close()
    return render_template('signup.html')
@app.route('/')
def index():
    if 'username' not in session:
        flash('Please sign in to access the home page.', 'warning')
        return redirect(url_for('sign'))
    return render_template('index.html', username=session['username'])
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'username' not in session:
        flash('❌ You need to sign in to upload files.', 'danger')
        print("❌ ERROR: No user session detected.")
        return redirect(url_for('sign'))
    print(f"✅ Session Username: {session['username']}")
    if request.method == 'POST':
        file = request.files.get('file')  
        if not file:
            flash('⚠️ No file selected!', 'warning')
            print("❌ ERROR: No file received in request.")
            return redirect(url_for('upload'))
        filename = secure_filename(file.filename)
        if filename == '':
            flash('⚠️ Empty filename!', 'warning')
            print("❌ ERROR: Filename is empty.")
            return redirect(url_for('upload'))
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        try:
            file.save(file_path)
            print(f"📂 File saved at: {file_path}")
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()
            print(f"🔍 User fetched from DB: {user}")
            if user:
                user_id = user['id']
                print(f"✅ User ID Found: {user_id}")
                sql = "INSERT INTO uploads (user_id, filename) VALUES (%s, %s)"
                cursor.execute(sql, (user_id, filename))
                db.commit()
                print("✅ Insert Query Executed Successfully!")
                cursor.execute("SELECT * FROM uploads WHERE user_id = %s ORDER BY id DESC LIMIT 1", (user_id,))
                inserted_row = cursor.fetchone()
                print(f"✅ Inserted Row from DB: {inserted_row}")
                if inserted_row:
                    flash("✅ File uploaded and stored in database successfully!", "success")
                else:
                    flash("⚠️ File upload failed!", "danger")
                    print("❌ ERROR: Data not inserted properly in MySQL!")
            else:
                flash("❌ User not found in database!", "danger")
                print("❌ ERROR: User ID not found in MySQL!")
        except mysql.connector.Error as err:
            flash(f"⚠️ Database error: {err}", "danger")
            print(f"⚠️ MySQL Error: {err}")
        finally:
            cursor.close()
            db.close()
            print("ℹ️ Database connection closed.")
    return render_template('upload.html')
@app.route('/analysis')
def analysis():
    if 'username' not in session:
        flash('You need to sign in.', 'warning')
        return redirect(url_for('sign'))
    uploaded_data = session.get('uploaded_data', None)
    filename = session.get('filename', 'No file uploaded')
    return render_template('analysis.html', uploaded_data=uploaded_data, filename=filename)
@app.route('/chart')
def chart():
    if 'username' not in session:
        flash('You need to sign in to access this page.', 'warning')
        return redirect(url_for('sign'))
    return render_template('chart.html')
@app.route('/video')
def video():
    if 'username' not in session:
        flash('You need to sign in to access this page.', 'warning')
        return redirect(url_for('sign'))
    return render_template('video.html')
@app.route('/predict', methods=['GET', 'POST'])
def predict():
    if 'username' not in session:
        flash('You need to sign in to access this page.', 'warning')
        return redirect(url_for('sign'))
    if request.method == 'POST':
        soil_type = request.form.get('soil_type')
        season = request.form.get('season')
        district = request.form.get('district')
        state = 'Tamil Nadu'
        data = [[soil_type, season, state, district]]
        try:
            prediction = model.predict(data)
            predicted_crop = get_crop_details(prediction[0])
            db = get_db_connection()
            cursor = db.cursor(dictionary=True)
            cursor.execute("SELECT id FROM users WHERE username = %s", (session['username'],))
            user = cursor.fetchone()
            if user:
                user_id = user['id']
                cursor.execute("INSERT INTO predictions (user_id, soil_type, season, district, predicted_crop) VALUES (%s, %s, %s, %s, %s)",
                               (user_id, soil_type, season, district, predicted_crop['name']))
                db.commit()
                flash("Prediction stored successfully!", "success")
            else:
                flash("User not found!", "danger")
            cursor.close()
            db.close()
            return render_template('prediction.html', 
                                   soil_type=soil_type,
                                   season=season,
                                   state=state,
                                   district=district,
                                   crop_name=predicted_crop['name'] if predicted_crop else None,
                                   crop_season=predicted_crop['season'] if predicted_crop else None,
                                   chemical=predicted_crop['chemical'] if predicted_crop else None,
                                   duration=predicted_crop['duration'] if predicted_crop else None,
                                   description=predicted_crop['description'] if predicted_crop else None,
                                   crop_image=predicted_crop['image'] if predicted_crop else None)
        except Exception as e:
            flash(f"Error in prediction: {str(e)}", "danger")
            return redirect(url_for('predict'))  
    return render_template('predict.html')  
def get_crop_details(crop_name):
    crop_details = {
        'Tomato': {
            'name': "Tomato (Solanum lycopersicum)",
            'duration': "90-150 days for Maturity & Harvesting",
            'chemical': """Seedling stage: Apply fungicide (e.g., Mancozeb).
Vegetative stage: Use nitrogen-rich fertilizers (e.g., Urea).
Flowering stage: Apply phosphorous fertilizers (e.g., SSP).""",
            'season': "Kharif (June - September), Rabi (October - February)",
            'image': "/static/tomato.jpg",
            'description': "Tomato is a high-yielding variety suitable for waterlogged areas."
        },
        'Brinjal': {
            'name': "Brinjal (Solanum melongena)",
            'duration': "120-150 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply farmyard manure (FYM).
Vegetative stage: Apply nitrogen fertilizer (e.g., Urea) and fungicide (e.g., Carbendazim).
Flowering & Fruiting stage: Apply potassium (e.g., MOP) and insecticides (e.g., Chlorpyrifos).""",
            'season': "Kharif (June - September), Rabi (October - February)",
            'image': "/static/Brinjal.webp",
            'description': "Brinjal is grown in well-drained, sandy loam soils."
        },
        'Onion': {
            'name': "Onion (Allium cepa)",
            'duration': "90-150 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply phosphorus (e.g., DAP).
Vegetative stage: Apply nitrogen (e.g., Urea).
Bulbing stage: Apply potassium (e.g., MOP).""",
            'season': "Rabi (October - March), Summer (March - June)",
            'image': "/static/Onion.jpg",
            'description': "Onions thrive in loamy soil with good drainage."
        },
        'Cabbage': {
            'name': "Cabbage (Brassica oleracea)",
            'duration': "90-180 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply 15-20 tons of organic manure.
Vegetative stage: Apply nitrogen fertilizer (e.g., Urea).
Head formation: Apply phosphorus (e.g., DAP) and potassium (e.g., MOP).
Pest/Disease control: Apply pesticides (e.g., Lambda-cyhalothrin) to manage pests.""",
            'season': "Kharif (June - September), Rabi (October - February)",
            'image': "/static/Cabbage.jpg",
            'description': "Cabbage grows well in fertile, well-drained sandy loam soil."
        },
        'Carrot': {
            'name': "Carrot (Daucus carota)",
            'duration': "80-120 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply farmyard manure (FYM).
Vegetative stage: Apply nitrogen fertilizer (e.g., Urea).
Root development: Apply potassium fertilizers (e.g., Potassium nitrate).
Pest/Disease control: Apply insecticides (e.g., Endosulfan).""",
            'season': "Winter (October - February)",
            'image': "/static/Carrot.avif",
            'description': "Carrots thrive in sandy loam or loamy soils."
        },
        'Banana': {
            'name': "Banana (Musa spp.)",
            'duration': "9-12 months for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply organic manure.
Vegetative growth: Use nitrogen and potassium.
Flowering & Fruiting: Apply balanced NPK.
Pest/Disease control: Use fungicides (e.g., Propiconazole).""",
            'season': "All year-round",
            'image': "/static/Banana.webp",
            'description': "Bananas require deep, well-drained alluvial soils."
        },
        'Mango': {
            'name': "Mango (Mangifera indica)",
            'duration': "3-6 months for Maturity & Harvesting",
            'chemical': """Pre-flowering: Use potassium fertilizers.
Flowering: Use potassium and magnesium sprays.
Post-flowering: Apply phosphorus fertilizers.
Pest/Disease control: Use Cypermethrin for pests.""",
            'season': "Summer (March - June)",
            'image': "/static/Mango.jpg",
            'description': "Mangoes thrive in well-drained sandy loam."
        },
        'Papaya': {
            'name': "Papaya (Carica papaya)",
            'duration': "9-12 months for Maturity & Harvesting",
            'chemical': """Pre-planting:Apply well-rotted manure and compost.
Vegetative growth: Apply nitrogen (e.g., Urea).
Flowering & Fruiting: Use balanced NPK fertilizers.
Pest/Disease control: Apply fungicides (e.g., Mancozeb).""",
            'season': "Throughout the year",
            'image': "/static/Papaya.jpeg",
            'description': "Papayas require well-drained sandy loam soil and grow year-round."
        },
        'Guava': {
            'name': "Guava (Psidium guajava)",
            'duration': "3-4 years for Maturity & Harvesting",
            'chemical': """Pre-planting: Incorporate organic matter and micro-nutrients.
Vegetative growth: Apply nitrogen and potassium fertilizers.
Flowering & Fruiting: Apply phosphatic fertilizers to encourage fruit development.
Pest/Disease control: Apply insecticides (e.g., Dimethoate).""",
            'season': " Kharif (June - September)",
            'image': "/static/Guava.webp",
            'description': "Guava (Psidium guajava) is a hardy tropical fruit that thrives in well-drained, loamy soils."
        },
        'Pineapple': {
            'name': "Pineapple (Ananas comosus)",
            'duration': "18-24 months for Maturity & Harvesting",
            'chemical': """Pre-planting: Incorporate farmyard manure (FYM) and organic compost.
Vegetative growth: Apply nitrogen (e.g., Urea) and potassium fertilizers.
Flowering & Fruiting: Apply phosphorus (e.g., SSP) and potassium-based fertilizers.
Pest/Disease control: Apply insecticides (e.g., Imidacloprid) to manage.""",
            'season': "Summer (March - June)",
            'image': "/static/Pineapple.jpeg",
            'description': "Pineapple (Ananas comosus) is a tropical fruit known for its sweet and tangy flavor."
        },
        'Potato': {
            'name': "Potato (Solanum tuberosum)",
            'duration': "90-120 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Use a fungicide like Mancozeb to prevent seed tuber diseases.
Vegetative growth: Apply nitrogen fertilizer (e.g., Urea) for leaf and stem growth.
Tuber development: Apply phosphorus (e.g., SSP) and potassium fertilizers (e.g., MOP).
Pest/Disease control: Use insecticides (e.g., Imidacloprid) to control aphids and potato tuber moth.""",
            'season': "Rabi (November - March), Summer (March - May)",
            'image': "/static/Potato.webp",
            'description': "Potato (Solanum tuberosum) is a versatile root vegetable widely cultivated for its nutritional and culinary value."
        },
        'Rice': {
            'name': "Rice (Oryza sativa)",
            'duration': "120 to 180 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply herbicides (e.g., Glyphosate).
Vegetative stage : Apply nitrogen fertilizers (e.g., Urea) for healthy growth.
Flowering & Grain filling : Apply micronutrients (e.g., Zinc sulfate).
Pest/Disease control: Apply pesticides (e.g., Chlorpyrifos) .""",
            'season': "Kharif (June - November), Rabi (November - March)",
            'image': "/static/Rice.jpg",
            'description': "Rice (Oryza sativa) is a staple food crop that feeds billions worldwide."
        },
        'Green Chilies': {
            'name': "Green Chilies (Capsicum annuum)",
            'duration': "90-150 days for Maturity & Harvesting",
            'chemical': """Pre-planting: Apply fungicides (e.g., Mancozeb) .
Vegetative growth (7-30 days): Apply nitrogen fertilizer (e.g., Urea) for healthy foliage.
Flowering & Fruiting : Apply phosphorous (e.g., SSP) and potassium fertilizers.
Pest/Disease control: Apply insecticides (e.g., Imidacloprid)  Fungicides (e.g., Carbendazim).""",
            'season': "Kharif (June - September), Rabi (October - February)",
            'image': "/static/Chilies.jpg",
            'description': "Green chilies (Capsicum annuum) are a popular vegetable and spice crop, valued for their pungency and vibrant flavor."
        },
        'Tea': {
            'name': "Tea (Camellia sinensis)",
            'duration': "3-4 years for Maturity & Harvesting",
            'chemical': """Pre-planting : Apply FYM or compost before planting.
Young plants: Use a nitrogen fertilizer (e.g., Urea).
Mature plants: Apply balanced NPK (e.g., 20:20:20).
Pest/Disease control: Apply insecticides (e.g., Imidacloprid) and fungicides (e.g., Mancozeb).""",
            'season': "Throughout the year, with peak growth in monsoon (June - September)",
            'image': "/static/Tea.jpg",
            'description': "Tea (Camellia sinensis) is a globally significant beverage crop known for its aromatic leaves, which are processed into black, green."
        },
    }
    return crop_details.get(crop_name, None)
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('sign'))
if __name__ == '__main__':

   app.run(host='0.0.0.0', port=5000, debug=True)
