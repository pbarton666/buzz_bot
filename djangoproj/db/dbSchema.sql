-- MySQL dump 10.11
--
-- Host: localhost    Database: testdb
-- ------------------------------------------------------
-- Server version	5.0.51a-3ubuntu5.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `_url_search`
--

DROP TABLE IF EXISTS `_url_search`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `_url_search` (
  `id` int(11) NOT NULL,
  `urlid` int(11) default NULL,
  `source` varchar(150) NOT NULL,
  `depth` int(11) default NULL,
  `urlorder` int(11) default NULL,
  `searchid` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `_url_search_urlid` (`urlid`),
  KEY `_url_search_searchid` (`searchid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `_url_tags`
--

DROP TABLE IF EXISTS `_url_tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `_url_tags` (
  `id` int(11) NOT NULL,
  `urlid` int(11) NOT NULL,
  `name` varchar(150) NOT NULL,
  `value` varchar(150) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `_url_tags_urlid` (`urlid`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(80) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL auto_increment,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `group_id` (`group_id`,`permission_id`),
  KEY `permission_id_refs_id_5886d21f` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_message`
--

DROP TABLE IF EXISTS `auth_message`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_message` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `message` longtext NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `auth_message_user_id` (`user_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(50) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `content_type_id` (`content_type_id`,`codename`),
  KEY `auth_permission_content_type_id` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=121 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL auto_increment,
  `username` varchar(30) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(30) NOT NULL,
  `email` varchar(75) NOT NULL,
  `password` varchar(128) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `last_login` datetime NOT NULL,
  `date_joined` datetime NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_id` (`user_id`,`group_id`),
  KEY `group_id_refs_id_f116770` (`group_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL auto_increment,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `user_id` (`user_id`,`permission_id`),
  KEY `permission_id_refs_id_67e79cb` (`permission_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_badUrlFragment`
--

DROP TABLE IF EXISTS `buzzapp_badUrlFragment`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_badUrlFragment` (
  `id` int(11) NOT NULL auto_increment,
  `badString` varchar(100) NOT NULL,
  `reason` varchar(100) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=19 DEFAULT CHARSET=latin1 COMMENT='criteria for rejecting a url based on its name';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_content`
--

DROP TABLE IF EXISTS `buzzapp_content`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_content` (
  `id` int(11) NOT NULL auto_increment,
  `content` text character set latin1,
  `dateAcquired` datetime default NULL,
  `datePosted` datetime default NULL,
  `shortCont` varchar(50) character set latin1 default NULL,
  `criteriaid` int(11) default NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `shortCont` (`shortCont`,`criteriaid`),
  KEY `fk_content_criteria` (`criteriaid`),
  CONSTRAINT `fk_content_criteria` FOREIGN KEY (`criteriaid`) REFERENCES `buzzapp_search_viewcriteria` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=13719 DEFAULT CHARSET=utf8 COMMENT='unique key only works on VARCHAR (not text) then only for VA';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_content_search`
--

DROP TABLE IF EXISTS `buzzapp_content_search`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_content_search` (
  `id` int(11) NOT NULL auto_increment,
  `searchid` int(11) NOT NULL,
  `contentid` int(11) NOT NULL,
  `urlid` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `ixsearch` (`searchid`),
  KEY `ixcont` (`contentid`),
  KEY `ixurl` (`urlid`),
  CONSTRAINT `urlcontsrch_cont` FOREIGN KEY (`contentid`) REFERENCES `buzzapp_content` (`id`) ON DELETE CASCADE,
  CONSTRAINT `urlcontsrch_srch` FOREIGN KEY (`searchid`) REFERENCES `buzzapp_search` (`id`) ON DELETE CASCADE,
  CONSTRAINT `urlcontsrch_url` FOREIGN KEY (`urlid`) REFERENCES `buzzapp_url` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6964 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_metasearch_search`
--

DROP TABLE IF EXISTS `buzzapp_metasearch_search`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_metasearch_search` (
  `id` int(11) NOT NULL auto_increment,
  `searchid` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `searchid` (`searchid`),
  CONSTRAINT `fk_metasearch_search` FOREIGN KEY (`searchid`) REFERENCES `buzzapp_search` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_negationwords`
--

DROP TABLE IF EXISTS `buzzapp_negationwords`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_negationwords` (
  `id` int(11) NOT NULL auto_increment,
  `word` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_negwords`
--

DROP TABLE IF EXISTS `buzzapp_negwords`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_negwords` (
  `id` int(11) NOT NULL auto_increment,
  `word` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8511 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_obscenewords`
--

DROP TABLE IF EXISTS `buzzapp_obscenewords`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_obscenewords` (
  `id` int(11) NOT NULL auto_increment,
  `word` varchar(50) default NULL,
  `defnum` int(11) default NULL,
  `worddef` varchar(300) default NULL,
  `pctthisdef` int(11) default NULL,
  `wordatts` varchar(300) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1601 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_poswords`
--

DROP TABLE IF EXISTS `buzzapp_poswords`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_poswords` (
  `id` int(11) NOT NULL auto_increment,
  `word` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=7423 DEFAULT CHARSET=utf8;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_scoremethods`
--

DROP TABLE IF EXISTS `buzzapp_scoremethods`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_scoremethods` (
  `id` int(11) NOT NULL auto_increment,
  `equation` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_scores`
--

DROP TABLE IF EXISTS `buzzapp_scores`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_scores` (
  `id` int(11) NOT NULL auto_increment,
  `methodid` int(11) default NULL,
  `contentid` int(11) default NULL,
  `score` float default NULL,
  PRIMARY KEY  (`id`),
  KEY `fk_scores_content` (`contentid`),
  KEY `fk_scores_scoremethod` (`methodid`),
  CONSTRAINT `fk_scores_content` FOREIGN KEY (`contentid`) REFERENCES `buzzapp_content` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_scores_scoremethod` FOREIGN KEY (`methodid`) REFERENCES `buzzapp_scoremethods` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9941 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_search`
--

DROP TABLE IF EXISTS `buzzapp_search`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_search` (
  `id` int(11) NOT NULL auto_increment,
  `include` varchar(255) default NULL,
  `exclude` varchar(255) default NULL,
  `clearAll` tinyint(1) default NULL COMMENT 'user request to clear results',
  `clearNonconform` tinyint(1) default NULL,
  `viewcriteriaid` int(11) default NULL,
  `andOr` varchar(5) default 'or',
  `deleteMe` tinyint(1) default '0',
  `userid` int(11) default '-1',
  `name` varchar(50) default NULL,
  PRIMARY KEY  (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=117 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_search_viewcriteria`
--

DROP TABLE IF EXISTS `buzzapp_search_viewcriteria`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_search_viewcriteria` (
  `id` int(11) NOT NULL auto_increment,
  `searchid` int(11) NOT NULL,
  `include` varchar(255) NOT NULL,
  `exclude` varchar(255) default NULL,
  `andOr` varchar(10) NOT NULL default 'or',
  `isPublic` tinyint(1) default '1',
  `title` varchar(50) default NULL,
  PRIMARY KEY  (`id`),
  KEY `searchid` (`searchid`),
  CONSTRAINT `fk_search_vie2` FOREIGN KEY (`searchid`) REFERENCES `buzzapp_search` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_url`
--

DROP TABLE IF EXISTS `buzzapp_url`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_url` (
  `id` int(11) NOT NULL auto_increment,
  `url` varchar(200) character set latin1 NOT NULL,
  `add_date` datetime default NULL,
  `url_order` mediumint(9) default NULL,
  `delete_me` tinyint(1) default NULL,
  `visit_date` datetime default NULL,
  `source` varchar(50) character set latin1 default NULL,
  `readFailures` int(11) default '0',
  `readSuccesses` int(11) default '0',
  PRIMARY KEY  (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=12322 DEFAULT CHARSET=utf8 ROW_FORMAT=DYNAMIC;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_url_html`
--

DROP TABLE IF EXISTS `buzzapp_url_html`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_url_html` (
  `id` int(11) NOT NULL auto_increment,
  `urlid` int(11) default NULL,
  `html` mediumtext,
  PRIMARY KEY  (`id`),
  KEY `urlid` (`urlid`),
  KEY `urlid_2` (`urlid`),
  CONSTRAINT `buzzapp_url_html_ibfk_1` FOREIGN KEY (`urlid`) REFERENCES `buzzapp_url` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1924 DEFAULT CHARSET=latin1 ROW_FORMAT=DYNAMIC;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_url_search`
--

DROP TABLE IF EXISTS `buzzapp_url_search`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_url_search` (
  `id` int(11) NOT NULL auto_increment,
  `urlid` int(11) default NULL,
  `source` varchar(50) default NULL,
  `depth` int(11) default NULL,
  `urlorder` int(11) default NULL,
  `searchid` int(11) default NULL,
  PRIMARY KEY  (`id`),
  KEY `urlid` (`urlid`),
  KEY `urlid_2` (`urlid`),
  KEY `fk_urlsearch_search` (`searchid`),
  CONSTRAINT `fk_urlsearch_search` FOREIGN KEY (`searchid`) REFERENCES `buzzapp_search` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_urlsearch_url` FOREIGN KEY (`urlid`) REFERENCES `buzzapp_url` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=9925 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_url_tags`
--

DROP TABLE IF EXISTS `buzzapp_url_tags`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_url_tags` (
  `id` int(11) NOT NULL auto_increment,
  `urlid` int(11) NOT NULL,
  `name` varchar(50) default NULL,
  `value` varchar(50) default NULL,
  PRIMARY KEY  (`id`),
  KEY `buzzapp_url_tags_url_id` (`urlid`),
  KEY `urlid` (`urlid`),
  CONSTRAINT `fk_urltags_url` FOREIGN KEY (`urlid`) REFERENCES `buzzapp_url` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6680 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `buzzapp_wordcount`
--

DROP TABLE IF EXISTS `buzzapp_wordcount`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `buzzapp_wordcount` (
  `id` int(11) NOT NULL auto_increment,
  `pos` int(11) default NULL,
  `neg` int(11) NOT NULL,
  `obscene` int(11) NOT NULL,
  `contentid` int(11) NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `fk_wordcount_content` (`contentid`),
  CONSTRAINT `fk_wordcount_content` FOREIGN KEY (`contentid`) REFERENCES `buzzapp_content` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4971 DEFAULT CHARSET=latin1 COMMENT='tracks count of words (pos, neg, etc.) in each content block';
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL auto_increment,
  `action_time` datetime NOT NULL,
  `user_id` int(11) NOT NULL,
  `content_type_id` int(11) default NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  PRIMARY KEY  (`id`),
  KEY `django_admin_log_user_id` (`user_id`),
  KEY `django_admin_log_content_type_id` (`content_type_id`)
) ENGINE=MyISAM AUTO_INCREMENT=3 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL auto_increment,
  `name` varchar(100) NOT NULL,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY  (`id`),
  UNIQUE KEY `app_label` (`app_label`,`model`)
) ENGINE=MyISAM AUTO_INCREMENT=41 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime NOT NULL,
  PRIMARY KEY  (`session_key`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;

--
-- Table structure for table `django_site`
--

DROP TABLE IF EXISTS `django_site`;
SET @saved_cs_client     = @@character_set_client;
SET character_set_client = utf8;
CREATE TABLE `django_site` (
  `id` int(11) NOT NULL auto_increment,
  `domain` varchar(100) NOT NULL,
  `name` varchar(50) NOT NULL,
  PRIMARY KEY  (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=2 DEFAULT CHARSET=latin1;
SET character_set_client = @saved_cs_client;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2010-03-02 17:56:06
