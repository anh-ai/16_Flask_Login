# Web Login

# Mục tiêu:
Dùng Flask, bootstrap5, html5, js, jquery, hãy viết một trang index và trang login, create user, database 
dùng SQLite có phân quyền User: Admin, Manager, Experts, Teacher, Supervisors, Learner, Guest, Block (trong `AiLibs/Flask_Login/templates/Modules/admin.html`) 


![img.png](static/images/img.png)

Pass mặc định: 123

# Yêu cầu:
- Đọc hiểu và có thể làm lại web này.
- Viết thêm module thay đổi thông tin cá nhân, đổi pass, có ảnh avatar (lưu thông tin user trong `static/users/...` nếu cần).

![img_1.png](static/images/img_1.png) 

# Cách làm chương trình hiện có:
Dưới đây là một ví dụ về cách sử dụng Flask, Bootstrap 5, HTML5, JavaScript và jQuery để tạo trang index, trang đăng nhập và trang tạo người dùng. Đây chỉ là một ví dụ cơ bản để bạn có thể bắt đầu, và có thể được tùy chỉnh và mở rộng theo nhu cầu của bạn.

Đầu tiên, cài đặt các thư viện cần thiết thông qua pip:

`pip install flask`


## Cài đặt:
```bash
pip install -r req.txt
```
hoặc vào trong thư mục `wheelhouse`, làm theo `Máy chạy:` trong  `readme.txt` trong đó.

## Run:
```bash
python app.py
```

## Tính năng chính của chương trình
Chương trình có các chức năng chính sau:
1. Quản lý User.
   - Đăng ký user.
   - Đăng nhập/đăng xuất.
   - Phân quyền: khi user hiện tại là admin thì menu này sẽ hiện lên.
   - Tự động lưu trạng thái đăng nhập của User ở phiên làm việc trước đó thời gian lưu là 3 tháng.
   - Cơ sở dữ liệu là SQLite3, có thể xoá file database đi để chương trình tự tạo file mới. Lúc này không có user mặc định. Cần set quyền admin trực tiếp trong DB.    
2. Hiển thị nội dung theo phân quyền

## Kỹ thuật code
1. Python Flask có dùng template
2. Python với database SQlite, lưu file ngay tại thư mục gốc
3. cách xử lý login/logout/create user
4. Cách lưu section, nhớ user đăng nhập để lần sau không cần đăng nhập nữa
5. Cách validate username/pass
6. Cách phân quyền cho entry point, kiểu như cần phải đăng nhập rồi mới chạy thì: `@login_required`, cần admin thì: `@admin_required`
7. Cách sử dụng template trong các folder khác nhau
8. Cách dùng file config, kết quả lưu vào yaml để dễ cấu hình, chỉnh sửa bằng tay
9. Templates:
    1. Cách dùng template đa tẩng (`ta_base.html` chứa khung => `index.html` chứa nội dung): dùng `{% extends "ta_base.html" -%}`
    2. Dùng `{% include "partials/Home.html" %}`: Trong `index.html` có chia html ra thành nhiều thành phần nhỏ, cái này không phải đa tầng, mà là phân chia nhỏ code
    3. Cách phân quyền trong template: `{% if session['role'] in ['Admin', 'Manager'] %}...{% else %}...{% endif %}`: nghĩa là user phải là 'Admin' hoặc 'Manager' thì mới làm gì đó, hoặc hiển thị nội dung theo user
    4. Cách dùng `macro` trong template (trong file `templates/partials/configs.html` và `templates/Modules/admin.html`)
        - Trong `configs.html` thì cách dùng đơn giản hơn, viết macro trong file đó rồi dùng luôn
        - Trong `admin.html` thì cao cấp hơn nhiều: `macro` được khai báo trong file riêng, thành thư viện dùng chung của cả hệ thống được. Có chỉ định tham số, có thể khai báo nhiều `macro`, và dùng 1 `macro` cho nhiều chức năng khác nhau được.
        - Filter: Trong file `admin.html` cũng có chức năng filter table, có thể lọc dữ liệu theo toàn bộ các cột hoặc 1 cột chỉ định trước.
+ Ajax: 
    * Trong file `templates/partials/configs.html` có hướng dẫn cách khai báo Ajax chuẩn và entry point của nó `url: '/update'` cùng cách lấy dữ liệu trên form, hiển thị alert trong js
    * trong file `admin.html` có khai báo 1 ajax tiêu chuẩn, có thể sử dụng tương tự cho các tác vụ khác
      



# Hướng dẫn sử dụng Macro, import, input trong Jinja2 template
Tham khảo [tại đây](https://jinja.palletsprojects.com/en/2.11.x/templates/#import)

1. viết code cho: `templates/taMacros.html`, code này cần bootstrap4/5 để chạy được.
```html
{% macro forminput(mID, mlabel, initValue, btnText, fnName="fnUpdate",label_width="auto", button_width="auto")%}
<form >
    <div class="input-group mt-4">
        <span class="input-group-text" style="width:{{label_width}};">{{mlabel}}</span>
        <input type="text" class="form-control" id="{{mID}}NameInput" value= "{{ initValue }}" required >
        <span class="input-group-text">
            <button type="button" class="btn btn-primary" onclick="{{fnName}}('{{mID}}')"  style="width:{{button_width}};">{{btnText}}</button>
        </span>
    </div>
</form>
<br>
{% endmacro %}
```

2. Trong file cần sử dụng, ví dụ: `templates/Modules/admin.html`, vì khác thư mục, nên import nó sẽ khác (cần lên thư mục cha).
```html
        {% import  "./taMacros.html" as forms %}
        {{ forms.forminput('search', 'Filter:', "", "Search" ) }}
```
3. 