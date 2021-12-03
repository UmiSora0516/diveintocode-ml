# from django.shortcuts import render
# from django.http import HttpRequest
# from django.core.files.storage import FileSystemStorage
from .yolov5 import detect
from django.conf import settings

import os
from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import UploadFileForm

from time import sleep
import chromedriver_binary
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

# Create your views here.

class_dic = {
    'Cabbage' : 'キャベツ',
    'Carrot' : 'にんじん',
    'Tomato' : 'トマト',
    'Potato' : 'じゃがいも',
    'Egg' : '卵',
    'Fish' : '魚',
    'Meet' : '肉',
    'Shrimp' : 'エビ',
    'Bell pepper' : 'ピーマン',
    'Onion' : '玉ねぎ'
}

class IndexView(TemplateView):

    template_name = 'index.hmtl'

    def get(self, request, *args, **kwargs):
        """GETリクエスト用のメソッド"""
        form = UploadFileForm
        return render(request, 'index.html', {"form": form})

    def post(self, request, *args, **kwargs):
        """POSTリクエスト用のメソッド"""
        recipes_dict = ''
        search_keywords = ''

        if "exe_detect" in request.POST:
            form = UploadFileForm(request.POST, request.FILES)

            if not form.is_valid():
                return render(request, 'index.html', {"form": form})

            filename_save = form.save()
            file_path = os.path.join(settings.MEDIA_ROOT, form.file_name)

            # YOLOで物体検出を実行
            pred, save_dir = detect.run(source=file_path,
                                        weights=settings.WEIGHTS_FILE,
                                        project=settings.YOLO_PROJECT_PATH
                                        )

            str_pred = ''
            for key, value in pred.items():
                buff_str = class_dic[key] + ' : ' + str(value) + ' '
                str_pred += ' ' + buff_str
                search_keywords += class_dic[key] + ' '

            # pred_img_path = os.path.join(save_dir, form.file_name)
            pred_img_path = os.path.join('media\yolo_out_dir', save_dir.stem, form.file_name)

            context = {
                'form': form,
                'filename_save': filename_save,
                'pred': str_pred,
                'pred_img_path': pred_img_path,
                'search_keywords': search_keywords
                # 'recipes_dict': recipes_dict
            }
            return render(request, 'index.html', context)

        elif "exe_search" in request.POST:
            form = UploadFileForm

            # 検索のテキストボックスから値を取得
            search_keywords = request.POST.get('search_keywords')
            keywords = request.POST.get('search_key')
            keywords = search_keywords + keywords
            recipes_dict = get_recipes(keywords)

            context = {
                'form': form,
                'filename_save': request.POST.get('filename_save'),
                'pred': request.POST.get('pred'),
                'pred_img_path': request.POST.get('pred_img_path'),
                'search_keywords': search_keywords,
                'recipes_dict': recipes_dict
            }
            return render(request, 'index.html', context)

        else:
            form = UploadFileForm(request.POST, request.FILES)

            if not form.is_valid():
                return render(request, 'index.html', {"form": form})

# -----------------------------------
# ログイン不要、本日の新着レシピを取得
# -----------------------------------
def get_recipes(keywords):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    # クックパッドを開く
    driver.get("https://cookpad.com/")
    # 検索テキストボックスの要素をid属性値から取得
    # search = driver.find_element_by_id("keyword")
    search = driver.find_element(by=By.ID, value="keyword")
    # 検索テキストボックスに"WebDriver"を入力
    search.send_keys(keywords)
    # Enterキーを押下して検索を実行
    # search.send_keys(Keys.ENTER)
    search.submit()

    sleep(1)
    # 検索結果からトップ3のレシピ情報を取得する。

    # 検索先のページのHTMLを取得
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    # TOP3のレシピを取得する
    top3_recipes = soup.find_all('div', class_='recipe-preview')[:3]

    recipe_dic = {}
    recipe_list = []
    for recipe in top3_recipes:
        recipe_dic['recipe_name'] = recipe.contents[3].a.string
        recipe_dic['href'] = 'http://cookpad.com' + recipe.contents[3].a.get('href')
        recipe_dic['src'] = recipe.contents[1].img.get('src')
        recipe_list.append(recipe_dic.copy())

    driver.close()
    driver.quit()

    return recipe_list

# -----------------------------------
# ログイン後に人気レシピを取得
# -----------------------------------
def get_recipes2(keywords):

    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    # クックパッドを開く
    # driver.get("https://cookpad.com/")
    # ログイン処理
    driver.get("https://cookpad.com/identity/session/new?navigator_name=cookpad&navigator_parameters%5Burl%5D=%2F")
    driver.find_element(by=By.XPATH, value="//*[@id='login_form']/div/form/div[1]/div[1]/input").send_keys("kanekohirama0130@gmail.com")
    driver.find_element(by=By.XPATH, value="//*[@id='login_form']/div/form/div[1]/div[2]/input").send_keys("kaneko0130")

    driver.find_element(by=By.CSS_SELECTOR, value="input.button.large").click()
    sleep(1)

    # 検索テキストボックスの要素をid属性値から取得
    # search = driver.find_element_by_id("keyword")
    search = driver.find_element(by=By.ID, value="keyword")
    # 検索テキストボックスに"WebDriver"を入力
    search.send_keys(keywords)
    # Enterキーを押下して検索を実行
    # search.send_keys(Keys.ENTER)
    search.submit()

    # 人気順をクリック
    driver.find_element(by=By.CLASS_NAME,  value="popularity").click()

    sleep(1)
    # 検索結果からトップ3のレシピ情報を取得する。

    # 検索先のページのHTMLを取得
    html = driver.page_source.encode('utf-8')
    soup = BeautifulSoup(html, 'html.parser')

    # TOP3のレシピを取得する
    top3_recipes = soup.find_all('div', class_='recipe-preview')[:3]

    recipe_dic = {}
    recipe_list = []
    for recipe in top3_recipes:
        recipe_dic['recipe_name'] = recipe.contents[3].a.string
        recipe_dic['href'] = 'http://cookpad.com' + recipe.contents[3].a.get('href')
        recipe_dic['src'] = recipe.contents[1].img.get('src')
        recipe_dic['description'] = recipe.contents[3].contents[7].getText().replace('\n', '')
        recipe_list.append(recipe_dic.copy())

    driver.close()
    driver.quit()

    return recipe_list
