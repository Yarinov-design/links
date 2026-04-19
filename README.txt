מה יש בחבילה הזאת

1. index.html
העמוד הראשי שלך

2. youtube.html
עמוד יוטיוב יפה עם fade ומקום ל 3 סרטונים אחרונים ו 3 שורטים אחרונים

3. assets/youtube-data.json
קובץ נתונים שהאתר טוען

4. scripts/update_youtube.py
סקריפט שמושך את הנתונים מיוטיוב

5. .github/workflows/update-youtube.yml
GitHub Action שמעדכן אוטומטית את youtube-data.json

מה אתה צריך לעשות אחרי העלאה ל GitHub
- להעלות את כל הקבצים כמו שהם
- ב GitHub להכנס ל Settings > Secrets and variables > Actions
- ליצור Secret חדש בשם YOUTUBE_API_KEY
- להכניס לשם את מפתח ה API שלך מיוטיוב
- להפעיל GitHub Actions בריפו

הערה חשובה
הזיהוי של Shorts פה הוא best effort
כרגע הוא מסמן Short אם הוא עד 3 דקות ויש בטייטל או בתיאור #shorts
