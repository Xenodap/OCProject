from django.db import models
from datetime import  datetime

class Board(models.Model):
    idx=models.AutoField(primary_key=True)
    writer=models.CharField(null=False,max_length=25)
    title=models.CharField(null=False,max_length=100)
    hit=models.IntegerField(default=0)
    content=models.TextField(null=False,max_length=1000)
    post_date=models.DateTimeField(default=datetime.now,blank=True)
    filename=models.CharField(null=True,blank=True,default="",max_length=500)
    filesize=models.IntegerField(default=0)
    down=models.IntegerField(default=0)

    def hit_up(self):
        self.hit +=1
    def down_up(self):
        self.down +=1

class comment(models.Model):
    idx=models.AutoField(primary_key=True)
    board_idx=models.IntegerField(null=False)
    writer=models.CharField(null=False,max_length=50)
    content=models.TextField(null=False)
    post_date=models.DateTimeField(default=datetime.now,blank=True)