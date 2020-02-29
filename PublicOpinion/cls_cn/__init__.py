# 财联社

# 部署
# 和整个舆情模块一起部署


# 监控:
# SELECT count(id) FROM cls_afterAfficheList WHERE pub_date > date_sub(CURDATE(), interval 1 day);
# SELECT count(id) FROM cls_depth_theme WHERE pub_date > date_sub(CURDATE(), interval 1 day);
# SELECT count(id) FROM cls_telegraphs  WHERE pub_date > date_sub(CURDATE(), interval 1 day);
