import datetime
from django import forms
from django.core.files.storage import default_storage


class UploadFileForm(forms.Form):
    file = forms.ImageField()
    file_name = None

    def save(self):
        """ファイルを保存するメソッド"""
        now_date = datetime.datetime.now().strftime('%Y%m%d%H%M%S')  # ファイル名に現在時刻を付与するため取得
        upload_file = self.files['file']  # フォームからアップロードファイルを取得
        self.file_name = default_storage.save(now_date + "_" + upload_file.name, upload_file)  # ファイルを保存 戻り値は実際に保存したファイル名
        # self.file_name = default_storage.save(upload_file.name, upload_file)  # ファイルを保存 戻り値は実際に保存したファイル名
        return default_storage.url(self.file_name)
