# 犀牛之星资讯
import base64
from urllib import parse

web_url = 'https://service.ipo3.com/Information/index'

ipo_api = 'https://api.ipo3.com/api/news_list?ipo3=l%2FJocdG1flWZ9o0XxuMfj9tqK9NvpC4UnocR78XeLYdzCTGD8CeeZYlsPiyksv1mgmWb7O37%2BRuWT%2FavUxAWdg%3D%3D'
ss = 'l%2FJocdG1flWZ9o0XxuMfj9tqK9NvpC4UnocR78XeLYdzCTGD8CeeZYlsPiyksv1mgmWb7O37%2BRuWT%2FavUxAWdg%3D%3D'
print(parse.unquote(ipo_api))

ret = {
    'data': "z/iX+6gBR1SphU+df+rfFbjKVs7onFsvZ+old/CywpeOZrflZq+Dm6wVqFcWq7HYaSLksGRGw9HtAeMfgduAiQ4ntGPGzAmzz0cEwbw1KU6qRfoJbT0rxCfSrca70EQzVlZxaDbp8NfBvbdtVsD1pakWbqzuqxb3zhlSfOymbLiIFYg0m3H2dDHoAg+QnT5YciXhYA/8831mG+J3QgANnVqok20mpEPQ70T8M8mycB3BRsyISjlC0l1pIGqCe27UXE6IiN58E/OQWoX5qdl5zyVkwWwacZGjnW9OL00ynN39DtLCABVLTHSXeoKuFB36hEW0+jFnFvX0h0e1R2DSPVSRX83zxOdho1V7IxSucchFC6AJg/n3bciDCXAxd7E/tZuAeR4rOiCqIN3EZVA3NIWsOivpRmg8qHtNuLHfhLbWYe8c93zNObFw9dvn9gq8CshYKyEFn6A3DGvWsJOLWTraBPosvlxLMFClzJAlqTC75oDQq94WLXezpQVkw7GGzDCp2SD0oppBgpwXb/ujk+f4BouyufwWahEi5JLXYvamcnZdizBfExleGNaOZ9J37qzaYF8Wot3pEgouxmyM5bTcBYOlvRQJKE2VH8ucz02edAvsB+Dzp+95LHxrMJEJMYyvIVNycVzW95iDU5ShtZp1zVS/X7EEesjpUwdQY7pkALKPcfh5BcNEXNvSzNJoQJiFGCcAVHzv+Ih7SALaoGaWk2CqgzVFXF8dicoke0oTJgdSjVfkH7YLUo1YriQXRpvuAdiFyoIdrm2/hM8aTnvixtPFI9RFCSQ0153qFwU+0qFLEWC4QUvhJIPu1Tzi8IoCm/86v3Tl1RgQke22RhEGrc//5R3ih4YjIC4KXoOG49b6z8rlIT8NhHos/d/8bCZ4w6+gpb2C071ZCoIsGJWi1qIlIy/JO1QkH5647nMvM5ZjNhHHhugat+LbF8/kJHStfwdjRr7wCZnfJvXwg0Xsx0XSo2zGGR4QbY321asosfv+kKbnO3muaI3ETGyNddvzk6dv6s+nTGzro/TvolrgVvMHGZtDZcjJdfyJ1sIrIb5IsBQPkry2bZVvjihgkoJqk2sHPc4b2od6HoVchvDSZKd0qa4/Ynr3ni5+RIM=",
    'msg': "success",
    'status': "1",
}
