USE comicdb

DROP TABLE IF EXISTS `comics`;
CREATE TABLE `comics` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `comic_name` char(128) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `episodes`;
CREATE TABLE `episodes` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `comic_id` int unsigned NOT NULL,
  `episode_name` char(64) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=873 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `images`;
CREATE TABLE `images` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `episode_id` int unsigned NOT NULL,
  `image_url` varchar(1024) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `comic_id` int unsigned NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=18420 DEFAULT CHARSET=utf8;
