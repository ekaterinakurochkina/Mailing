from django.db.models import BooleanField
from django.forms import ModelForm
from .models import Sending, Message, MailingRecipient
from django.core.exceptions import ValidationError

# forbidden = ['казино', 'криптовалюта', 'крипта', 'биржа',
#              'дешево', 'бесплатно', 'обман', 'полиция', 'радар']

class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs['class']="form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"
                field.widget.attrs["placeholder"] = field.label


class SendingForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Sending
        fields = "__all__"
    def create_owner(self):
        owner = self.request.user
        return owner

class SendingModeratorForm(StyleFormMixin, ModelForm):   # Класс для отображения сообщений для модератора
    class Meta:
        model = Sending
        fields = ["id", "status", "recipient", "message","owner", "start_sending", "end_sending"]

class MessageForm(StyleFormMixin, ModelForm):
    class Meta:
        model = Message
        fields = ['subject', 'message_body']


class MailingRecipientForm(StyleFormMixin, ModelForm):
    class Meta:
        model = MailingRecipient
        fields = ['email', 'name']



# class ProductForm(StyleFormMixin, forms.ModelForm):
#     class Meta:
#         model = Product
#         fields = ['name', 'description', 'image', 'category', 'price', 'created_at', 'is_published','owner']
#         exclude = ['created_at', 'updated_at']
#
#     def __init__(self, *args, **kwargs):
#         super(ProductForm, self).__init__(*args, **kwargs)
#         self.fields['name'].widget.attrs.update({
#             'class': 'form-control',  # Добавление CSS-класса для стилизации поля
#             'placeholder': 'Введите название продукта'  # Текст подсказки внутри поля
#         })
#         self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите описание'})
#         self.fields['image'].widget.attrs.update({'class': 'form-control'})
#         self.fields['category'].widget.attrs.update({'class': 'form-control'})
#         self.fields['price'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите цену'})
#         # self.fields['owner'].widget.attrs.update({'class': 'form-control'})
#         # self.fields['created_at'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите дату'})
#
#     def clean_name(self):
#         name = self.cleaned_data.get('name')
#         if any(word in name.lower() for word in forbidden):
#             raise ValidationError("Не используйте в названии запрещенные слова")
#         return name
#
#     def clean_description(self):
#         description = self.cleaned_data.get('description')
#         if any(word in description.lower() for word in forbidden):
#             raise ValidationError("Не используйте в описании запрещенные слова.")
#         return description
#
#     def clean_price(self):
#         price = self.cleaned_data.get('price')
#         if price < 0:
#             raise ValidationError("Цена не должна быть отрицательной")
#         return price
#
#     def clean_image(self):
#         image = self.cleaned_data.get('image')
#         if image:
#             if image.size > 5 * 1024 * 1025:
#                 raise ValidationError("Файл больше 5МБ")
#             if not (image.name.endswith('.jpg') or image.name.endswith('.jpeg') or image.name.endswith('.png')):
#                 raise ValidationError("Файл недопустимого формата")
#         return image
#
#     def create_owner(self):
#         owner = self.request.user
#         return owner
#
#
# class CategoryForm(StyleFormMixin, forms.ModelForm):
#     class Meta:
#         model = Category
#         fields = ['name', 'description']
#
# class ProductModeratorForm(StyleFormMixin, forms.ModelForm):   # Класс для отображения продукта для модератора
#     class Meta:
#         model = Product
#         fields = ['name', 'is_published', 'owner']
