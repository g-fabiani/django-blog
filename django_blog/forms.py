from django import forms
from .models import Post
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Field, Div, HTML, Submit
from crispy_forms.bootstrap import InlineCheckboxes, StrictButton, FormActions
from crispy_bootstrap5.bootstrap5 import Switch
from tinymce.widgets import TinyMCE
from django.utils.timezone import localtime

class PostCommonLayout(Layout):
    """Layout common for create and update form for posts"""
    def __init__(self, *args, **kwargs):
        super().__init__(
            "title",
            "subtitle",
            Field("body"),
        )

class PostCommonForm(forms.ModelForm):
    """Form for working with posts"""
    class Meta:
        model = Post
        fields = ["title", "subtitle", "body"]
        widgets = {
            'body': TinyMCE(),
        }


class PostChangeDateForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ["pub_date",]
        widgets = {
            'pub_date': forms.DateTimeInput(
                format=('%Y-%m-%dT%H:%M'),
                attrs={"type": "datetime-local"}
                ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        current_datetime = localtime().strftime("%Y-%m-%dT%H:%M")
        self.fields['pub_date'].widget.attrs['value'] = current_datetime
        self.fields['pub_date'].widget.attrs['min'] = current_datetime

        self.helper = FormHelper()
        self.helper.layout = Layout(
            "pub_date",
            HTML(f'<p class="form-text">Scegli quando vuoi che sia reso pubblico il post “{self.instance}”.</p>'),
            FormActions(
                Submit("submit", "Programma post"),
                HTML('<a href="{% url "post_detail" post.pk %}" class="btn btn-outline-danger">Annulla</a>')
            )
        )



class PostCreateForm(PostCommonForm):
    """Form for the creation of new posts"""

    author = forms.BooleanField(required=False, label="Pubblica a mio nome")

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_id = 'post-form'
        self.helper.layout = Layout(
            Div(
                Switch("author"),
                HTML("<p class='form-text'>Puoi decidere di pubblicare il post a tuo nome. In questo caso solo tu potrai modificarlo o eliminarlo</p>")
            ),
            Div(
                HTML('<label for="tag" class="form-label">Tag (<span id="tag-count">0</span>):</label>'
                    '<ul id="tag-list" class="post-meta mb-3"></ul>'
                    '<input type="text" name="tag" id="tag" list="tag-datalist" autocomplete="off" class="text-input form-control"'
                    'placeholder="Cerca o aggiungi un tag">'
                    '<datalist id="tag-datalist"></datalist>'),
                    css_class="mb-3"
            ),
            PostCommonLayout(),
            FormActions(
                StrictButton("Pubblica", name="submit", value="publish", type="submit", css_class="btn-success"),
                StrictButton("Salva Bozza", name="submit", value="draft", type="submit", css_class="btn-warning"),
                StrictButton("Programma", name="submit", value="set_date", type="submit", css_class="btn-secondary"),
                HTML('<a href="{% url "posts" %}" class="btn btn-outline-danger">Annulla</a>')
            ),
            HTML("<p class='form-text'>Puoi decidere di <strong>pubblicare</strong> il post immediatamente, <strong>salvarlo come bozza</strong>, oppure <strong>programmare la pubblicazione</strong> per una data successiva (che sarà sempre possibile cambiare)</p>")
        )


class PostUpdateForm(PostCommonForm):
    """Form for the update for posts"""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_id = 'post-form'
        self.helper.layout = Layout(
            Div(
                HTML('<label for="tag" class="form-label">Tag (<span id="tag-count">0</span>):</label>'
                    '<ul id="tag-list" class="post-meta mb-3"></ul>'
                    '<input type="text" name="tag" id="tag" list="tag-datalist" autocomplete="off" class="text-input form-control"'
                    'placeholder="Cerca o aggiungi un tag">'
                    '<datalist id="tag-datalist"></datalist>'),
                    css_class="mb-3"
            ),
            PostCommonLayout(),
            FormActions(
                StrictButton("Salva le modifiche", name="submit", value="save", type="submit", css_class="btn-success"),
                HTML('<a href="{% url "post_detail" post.pk %}" class="btn btn-outline-danger">Annulla</a>')

                )
            )

