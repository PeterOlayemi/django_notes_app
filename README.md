# 🧠 MindPad - Personal Notes & Analytics App

MindPad is a modern, full-featured Django web application for managing personal notes, files, and tags, with beautiful analytics and robust user authentication. Built for productivity, privacy, and insight, MindPad is perfect for anyone who wants a secure, extensible, and data-driven note-taking experience.

---

## 🚀 Features

- **Rich Note Editing:**  
  Create, edit, and organize notes with Markdown or rich text support.

- **Tagging System:**  
  Add multiple tags to notes for easy categorization and search.

- **File Attachments:**  
  Attach files to your notes and manage them securely.

- **Advanced Analytics:**  
  Analytics dashboard with interactive charts (Chart.js) showing:
  - Notes per month, per tag, per day
  - Top tags
  - Notes with/without attachments
  - Note status (active/archived)
  - Average note length
  - Tag diversity and more

- **User Authentication:**  
  Secure registration, login, password reset, and social login via [Django Allauth](https://django-allauth.readthedocs.io/).

- **Dark Mode:**  
  Seamless light/dark theme toggle with Tailwind CSS and Alpine.js.

- **Responsive Design:**  
  Mobile-friendly UI with Tailwind CSS.

- **Security:**  
  Notes are private to each user. Attachments are stored securely.

---

## 🛠️ Tech Stack

- **Backend:** Django 4+, Django Allauth, django-taggit
- **Frontend:** Tailwind CSS, Alpine.js, Chart.js
- **Database:** SQLite (default, easy to swap for PostgreSQL/MySQL)
- **Other:** Python 3.10+, HTML5, JavaScript

---

## 📦 Installation & Setup

### 1. Clone the Repository

```sh
git clone https://github.com/PeterOlayemi/django_notes_app.git
cd mindpad
```

### 2. Create and Activate a Virtual Environment

```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Django Allauth Setup

- Allauth is pre-configured for email/password and social login.
- Update `django_notes_app/settings.py` with your email backend and social providers if needed.
- Run migrations:

```sh
python manage.py migrate
```

- Create a superuser:

```sh
python manage.py createsuperuser
```

### 5. Collect Static Files

```sh
python manage.py collectstatic
```

### 6. Run the Development Server

```sh
python manage.py runserver
```

### 7. Access the App

- Visit [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to use MindPad.
- Visit `/admin/` for the Django admin.

---

## ⚙️ Configuration

- **Environment Variables:**  
   Create a `.env` file in the project root with the following variables:
   ```
   SECRET_KEY = your-django-secret-key
   email = your-email@example.com
   appPassword = your-app-specific-password
   ```

   - `SECRET_KEY`: Your Django secret key (generate with `python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'`)
   - `email`: The email address used for sending emails (e.g., for password reset, newsletter)
   - `appsPassword`: The app-specific password for your email provider (e.g., Gmail App Password)

- **Media & Attachments:**  
  Uploaded files are stored in `/media/attachments/`.  
  Make sure your server serves media files in production.

- **Social Auth:**  
  Configure social providers in the Django admin under "Social applications".

---

## 📊 Analytics Dashboard

MindPad includes a dedicated analytics page (`/notes/analytics/`) with interactive charts and stats about your notes, tags, and activity.  
Great for personal insight and portfolio demonstration!

---

## 📝 Customization

- **Themes:** Easily customize Tailwind CSS for your own color scheme.
- **Extend Models:** Add more fields to notes, tags, or users as needed.
- **APIs:** Build REST APIs with Django REST Framework for mobile or integrations.

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

This project is licensed under [MIT License](LICENSE).

---

## 🙌 Credits

- [Django](https://www.djangoproject.com/)
- [Django Allauth](https://django-allauth.readthedocs.io/)
- [django-taggit](https://django-taggit.readthedocs.io/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Alpine.js](https://alpinejs.dev/)
- [Chart.js](https://www.chartjs.org/)

---

> **MindPad** – Your notes, your insights, your way.
