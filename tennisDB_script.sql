CREATE TABLE `match` (
  `match_id` int NOT NULL AUTO_INCREMENT,
  `id_tg_user` bigint DEFAULT NULL,
  `date_booking` varchar(40) DEFAULT NULL,
  `date_without_booking` varchar(40) DEFAULT NULL,
  `comment` varchar(300) DEFAULT NULL,
  `player_1` bigint DEFAULT NULL,
  `player_2` bigint DEFAULT NULL,
  PRIMARY KEY (`match_id`),
  KEY `match_users_fk` (`id_tg_user`),
  CONSTRAINT `match_users_fk` FOREIGN KEY (`id_tg_user`) REFERENCES `users` (`tg_user_id`)
);

CREATE TABLE `division` (
  `division_id` int NOT NULL,
  `name_division` varchar(20) NOT NULL,
  PRIMARY KEY (`division_id`)
);

CREATE TABLE `tournament` (
  `tournament_id` int NOT NULL AUTO_INCREMENT,
  `name_tournament` varchar(50) DEFAULT NULL,
  `division` varchar(15) DEFAULT NULL,
  `quantity_person` int DEFAULT NULL,
  `start_tournament` varchar(10) DEFAULT NULL,
  `end_tournament` varchar(10) DEFAULT NULL,
  `price` int DEFAULT NULL,
  `link_table` varchar(120) DEFAULT NULL,
  `regulations` text(2500) DEFAULT NULL,
  PRIMARY KEY (`tournament_id`)
);

CREATE TABLE `tournament_players` (
  `id_tournament_players` int NOT NULL AUTO_INCREMENT,
  `id_tournament` int DEFAULT NULL,
  `id_tg_user` bigint DEFAULT NULL,
  PRIMARY KEY (`id_tournament_players`),
  KEY `tournament_players_tournament_fk` (`id_tournament`),
  KEY `tournament_players_users_fk` (`id_tg_user`),
  CONSTRAINT `tournament_players_tournament_fk` FOREIGN KEY (`id_tournament`) REFERENCES `tournament` (`tournament_id`),
  CONSTRAINT `tournament_players_users_fk` FOREIGN KEY (`id_tg_user`) REFERENCES `users` (`tg_user_id`)
);

CREATE TABLE `users` (
  `tg_user_id` bigint NOT NULL,
  `name_user` varchar(20) DEFAULT NULL,
  `link` varchar(30) DEFAULT NULL,
  `age` int DEFAULT NULL,
  `sex` varchar(10) DEFAULT NULL,
  `division_level` int DEFAULT NULL,
  `ban_status` tinyint(1) DEFAULT NULL,
  `end_date_ban` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`tg_user_id`),
  UNIQUE KEY `tg_user_id` (`tg_user_id`),
  KEY `users_division_fk` (`division_level`),
  CONSTRAINT `users_division_fk` FOREIGN KEY (`division_level`) REFERENCES `division` (`division_id`)
);

CREATE TABLE `inventory` (
  `inventory_id` int NOT NULL AUTO_INCREMENT,
  `photo` varchar(30) DEFAULT NULL,
  `description` varchar(250) DEFAULT NULL,
  PRIMARY KEY (`inventory_id`)
);

CREATE TABLE `fast_booking_players` (
  `user_id` int NOT NULL AUTO_INCREMENT,
  `tg_id_user` bigint DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `tg_id_user` (`tg_id_user`)
);

CREATE TABLE `payment` (
  `id_player` int NOT NULL AUTO_INCREMENT,
  `id_tournament` int DEFAULT NULL,
  `id_tg_user` bigint DEFAULT NULL,
  `price` int DEFAULT NULL,
  `photo` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id_player`),
  KEY `payment_players_tournament_fk` (`id_tournament`),
  KEY `payment_players_users_fk` (`id_tg_user`),
  CONSTRAINT `payment_players_tournament_fk` FOREIGN KEY (`id_tournament`) REFERENCES `tournament` (`tournament_id`),
  CONSTRAINT `payment_players_users_fk` FOREIGN KEY (`id_tg_user`) REFERENCES `users` (`tg_user_id`)
);