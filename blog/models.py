from django.db import models

class Blogpost(models.Model):
    post_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    head0 = models.CharField(max_length=500, default="")
    chead0 = models.TextField(default="")
    head1 = models.CharField(max_length=500, default="", blank=True)
    chead1 = models.TextField(default="", blank=True)
    head2 = models.CharField(max_length=500, default="", blank=True)
    chead2 = models.TextField(default="", blank=True)
    pub_date = models.DateField()
    thumbnail = models.ImageField(upload_to="shop/images", default="")

    def __str__(self):
        return self.title
