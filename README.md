# Codal-Fetcher
A Python bot to collect capital increase announcements from Codal.ir.


Codal Capital Increase Bot | ربات افزایش سرمایه کدال

A Python bot that collects capital increase announcements from [Codal.ir](https://www.codal.ir), the official disclosure site for Iranian stock market companies.

ربات پایتون برای جمع‌آوری اطلاعیه‌های افزایش سرمایه از سایت کدال، سامانه رسمی انتشار اطلاعات شرکت‌های بورسی ایران.

---

##  How It Works | نحوه عملکرد

  Fetches the latest capital increase announcement** from Codal.ir  
  دریافت آخرین اطلاعیه مرتبط با افزایش سرمایه از سایت کدال  

  Searches previous related announcements** using the permit/reference number  
  جست‌وجوی اطلاعیه‌های پیشین با استفاده از شماره مجوز مربوطه  

  Converts attached PDF files into images** for display or further processing  
  تبدیل فایل‌های PDF ضمیمه به تصویر جهت پردازش یا نمایش  

---

##  Features | امکانات

- Collects and filters capital increase announcements  
- Tracks related historical data  
- Converts PDF attachments to image format  
- Simple, customizable code structure  

- جمع‌آوری و فیلتر اطلاعیه‌های افزایش سرمایه  
- ردیابی سوابق مرتبط  
- تبدیل فایل‌های PDF ضمیمه به فرمت تصویر  
- ساختار کد ساده و قابل تنظیم  

---

##  Installation | نصب

### 1. Clone the repository
```
  git clone https://github.com/your-username/your-repo-name.git
  cd Codal-Fetcher
```

#Install Dependencies
```
  pip install -r requirements.txt
```

#Install Poppler
  On Windows:
    Download from: https://github.com/oschwartz10612/poppler-windows/releases

  On macOS:
    ```
    brew install poppler
    ```

  On Linux
    ```
    sudo apt install poppler-utils
    ```

#Configuration
  ```
  #In config.py 
  POPPLER_PATH = "" # Replace with your actual path
  ```

