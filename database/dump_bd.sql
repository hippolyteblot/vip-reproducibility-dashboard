-- MySQL dump 10.13  Distrib 8.0.33, for Linux (x86_64)
--
-- Host: localhost    Database: dashboard
-- ------------------------------------------------------
-- Server version	8.0.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `dashboard`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `dashboard` /*!40100 DEFAULT CHARACTER SET utf8mb3 */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `dashboard`;

--
-- Table structure for table `app_version`
--

DROP TABLE IF EXISTS `app_version`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `app_version` (
  `id` int NOT NULL AUTO_INCREMENT,
  `number` varchar(45) NOT NULL,
  `application_id` int NOT NULL,
  `girder_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `app_version`
--

LOCK TABLES `app_version` WRITE;
/*!40000 ALTER TABLE `app_version` DISABLE KEYS */;
INSERT INTO `app_version` VALUES (9,'1.3',6,'644a372385f48d3da071405d'),(10,'1.4',6,'6449163285f48d3da0713574'),(11,'1.5',6,'644a450e85f48d3da07145e2'),(12,'1.9.0',7,'646c6b6285f48d3da0718cb0');
/*!40000 ALTER TABLE `app_version` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `application`
--

DROP TABLE IF EXISTS `application`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `application` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `girder_id` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `application`
--

LOCK TABLES `application` WRITE;
/*!40000 ALTER TABLE `application` DISABLE KEYS */;
INSERT INTO `application` VALUES (6,'cquest','6449162485f48d3da0713573'),(7,'brats','646b6ae285f48d3da0718cad');
/*!40000 ALTER TABLE `application` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `experiment`
--

DROP TABLE IF EXISTS `experiment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `experiment` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `version_id` int NOT NULL,
  `parameter_id` varchar(45) DEFAULT NULL,
  `girder_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `experiment`
--

LOCK TABLES `experiment` WRITE;
/*!40000 ALTER TABLE `experiment` DISABLE KEYS */;
INSERT INTO `experiment` VALUES (5,'repro-exp',9,'2','644a374285f48d3da071405e'),(6,'exp-41',10,'2','644a5c5585f48d3da0714832'),(7,'exp-42',10,'2','6449164c85f48d3da0713575'),(8,'large-repro-test',11,'2','644a452e85f48d3da07145e3'),(10,'test-folder',12,'2','646c6b7b85f48d3da0718cb1'),(11,'quest_param_117T_A',11,NULL,'64808a59655dd021c0ae9345'),(12,'quest_param_117T_B',11,NULL,'64808a5f655dd021c0ae9346');
/*!40000 ALTER TABLE `experiment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `input`
--

DROP TABLE IF EXISTS `input`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `input` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `md5` varchar(45) NOT NULL,
  `girder_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `input`
--

LOCK TABLES `input` WRITE;
/*!40000 ALTER TABLE `input` DISABLE KEYS */;
INSERT INTO `input` VALUES (39,'Rec001_Vox2.mrui','87be369ab36eacba3996a0a24e339d27','63e0d46c0386da2747642016'),(40,'Rec012_Vox2.mrui','e3ce439ae97bac0655d7f4ad6348c3bb','63e0d4700386da2747642052'),(41,'Rec012_Vox1.mrui','ac5f49ff36a00ff96ebff3c4cd579b4b','63e0d4700386da274764204f'),(42,'Rec016_Vox2.mrui','ef07fcd245e61b50e0eb19629b6b42e7','63e0d4720386da2747642067'),(43,'Rec004_Vox2.mrui','cf728ccffcfc8de8a4aebcbc7c826700','63e0d46e0386da2747642025'),(44,'Rec009_Vox2.mrui','1efa9b823f3a41b7c66c3c01996435e0','63e0d46f0386da2747642040'),(45,'Rec007_Vox1.mrui','e3ae970d346dcde2328798b53604d69c','63e0d46e0386da2747642031'),(46,'Rec008_Vox2.mrui','d70b55e9e424c9d9fdb7aaaeb4fcd728','63e0d46f0386da274764203a'),(47,'Rec014_Vox2.mrui','7c55502f0d2233ed26a86801071edc0a','63e0d4710386da274764205b'),(48,'Rec013_Vox1.mrui','de0f3a04979adebe50f772537a64531b','63e0d4710386da2747642055'),(49,'Rec006_Vox1.mrui','ef95fa0360de303580b6c4590881f3c7','63e0d46e0386da274764202e'),(50,'Rec017_Vox2.mrui','3a099acb806ea7e41df4f27e22d21e68','63e0d4720386da274764206d'),(51,'Rec020_Vox1.mrui','f843769193b713c8453a1ca9fe9f589b','63e0d4730386da2747642079'),(52,'Rec021_Vox1.mrui','fada97d0d411783fcb4f94547909bca4','63e0d4730386da274764207f'),(53,'Rec021_Vox2.mrui','40aa4012b0245009561c540957dcb805','63e0d4730386da2747642082'),(54,'Rec007_Vox2.mrui','f145501263612182a41015206c842144','63e0d46f0386da2747642034'),(55,'Rec005_Vox2.mrui','5b39668e8e390b94d47e8496103a30bd','63e0d46e0386da274764202b'),(56,'Rec017_Vox1.mrui','c436fa07d6b3dd37fc6793d3f38120e2','63e0d4720386da274764206a'),(57,'Rec005_Vox1.mrui','a600c27a83b27b05f151cb8d131d4454','63e0d46e0386da2747642028'),(58,'Rec019_Vox1.mrui','bf83b073b5421911e9ace9f678f8572b','63e0d4730386da2747642076'),(59,'Rec010_Vox2.mrui','c0f9a07b521c9bd70e7624eb0d603370','63e0d4700386da2747642046'),(60,'Rec003_Vox2.mrui','2688bc660754f22a304090771f1ae952','63e0d46d0386da274764201f'),(61,'Rec008_Vox1.mrui','7fb62e71d409e15d4535960e2274b82d','63e0d46f0386da2747642037'),(62,'Rec020_Vox2.mrui','0b74d75ff8e9361b0febcf17c7f8bb62','63e0d4730386da274764207c'),(63,'Rec010_Vox1.mrui','d9e18575112ed5168398fd7794307722','63e0d4700386da2747642043'),(64,'Rec018_Vox1.mrui','5a3b2bcf6b5b31af267f6e45b3781293','63e0d4720386da2747642070'),(65,'Rec011_Vox2.mrui','ef96ecc642699ed6dc576587dc9fb370','63e0d4700386da274764204c'),(66,'Rec015_Vox2.mrui','65d335cc7ee958270b4144ba1c36a709','63e0d4710386da2747642061'),(67,'Rec011_Vox1.mrui','5b646c4a5c666c286dd107d7c6305da1','63e0d4700386da2747642049'),(68,'Rec002_Vox1.mrui','deb82780a04d3df31aab5f3de36592ca','63e0d46d0386da2747642019'),(69,'Rec018_Vox2.mrui','5ad1a98b766d549ae22c1f1726aef035','63e0d4730386da2747642073'),(70,'Rec009_Vox1.mrui','f5ee049767bc66b4b9b07bd2989ae3ff','63e0d46f0386da274764203d'),(71,'Rec014_Vox1.mrui','4e2790fc48d1d4d4b20f59271e9e6f31','63e0d4710386da2747642058'),(72,'Rec001_Vox1.mrui','d9eaaae34b84d68cbc2e8844db3fd201','63e0d46c0386da2747642013'),(73,'Rec016_Vox1.mrui','7a94434ad16dc14301e4c9631d42a438','63e0d4720386da2747642064'),(74,'Rec004_Vox1.mrui','9c3585cefcfce56f1aa521e85c8da735','63e0d46d0386da2747642022'),(75,'Rec003_Vox1.mrui','23f9a5db0adaa5a02d2827f2cbcc07dc','63e0d46d0386da274764201c'),(76,'Rec015_Vox1.mrui','a1ef037615ff20ce5cd7c254f5de7f5c','63e0d4710386da274764205e'),(80,'T1.nii.gz','9e2e95cebdf12f00c3a43abe3ebff2d4','646dcb2185f48d3da0718f51');
/*!40000 ALTER TABLE `input` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `output`
--

DROP TABLE IF EXISTS `output`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `output` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `md5` varchar(45) NOT NULL,
  `workflow_id` varchar(45) NOT NULL,
  `input_id` varchar(45) NOT NULL,
  `girder_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=385 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `output`
--

LOCK TABLES `output` WRITE;
/*!40000 ALTER TABLE `output` DISABLE KEYS */;
INSERT INTO `output` VALUES (191,'Rec001_Vox2.mrui--quest_param_117T_B.txt.tgz','64dd835b3b5f9148483cfc895771881a','7','39','644a378a85f48d3da0714065'),(192,'Rec012_Vox2.mrui--quest_param_117T_B.txt.tgz','248687c09f844152e74612cf875e213a','7','40','644a378a85f48d3da071408d'),(193,'Rec012_Vox1.mrui--quest_param_117T_B.txt.tgz','1757684e142b5c8aa84cc260ab3b40c5','7','41','644a378a85f48d3da071408b'),(194,'Rec016_Vox2.mrui--quest_param_117T_B.txt.tgz','4ea138990551984050c26edfebf7a9cf','7','42','644a378a85f48d3da071409b'),(195,'Rec004_Vox2.mrui--quest_param_117T_B.txt.tgz','ba3c1d83c16db0031724e88cca1f335d','7','43','644a378a85f48d3da071406f'),(196,'Rec009_Vox2.mrui--quest_param_117T_B.txt.tgz','7b898e7ef6194830b3fb7365894bffb2','7','44','644a378a85f48d3da0714081'),(197,'Rec007_Vox1.mrui--quest_param_117T_B.txt.tgz','eef6aa76855c4213bb744e788ea1ee83','7','45','644a378a85f48d3da0714077'),(198,'Rec008_Vox2.mrui--quest_param_117T_B.txt.tgz','6f75b18dabf041df68a2984ad9d96d76','7','46','644a378a85f48d3da071407d'),(199,'Rec014_Vox2.mrui--quest_param_117T_B.txt.tgz','d60b8cd4cd133ca249efde1a49b0526c','7','47','644a378a85f48d3da0714093'),(200,'Rec013_Vox1.mrui--quest_param_117T_B.txt.tgz','50642a1fc1a0467a27c20c4075a2e3bb','7','48','644a378a85f48d3da071408f'),(201,'Rec006_Vox1.mrui--quest_param_117T_B.txt.tgz','2d3f3b31db239f858324afbe407a971c','7','49','644a378a85f48d3da0714075'),(202,'Rec017_Vox2.mrui--quest_param_117T_B.txt.tgz','fe7081796cbaf3e1fcb7e6345889b8fd','7','50','644a378b85f48d3da071409f'),(203,'Rec020_Vox1.mrui--quest_param_117T_B.txt.tgz','82de285ceefe66a941ecbb85284d898a','7','51','644a378b85f48d3da07140a7'),(204,'Rec021_Vox1.mrui--quest_param_117T_B.txt.tgz','86dda5b27870854261f643237ded8564','7','52','644a378b85f48d3da07140ab'),(205,'Rec021_Vox2.mrui--quest_param_117T_B.txt.tgz','ffc0cecd2bc2a197db72c6cbbe6b17f4','7','53','644a378b85f48d3da07140ad'),(206,'Rec007_Vox2.mrui--quest_param_117T_B.txt.tgz','731ba37c0c7f3a0a41d5df7791979f1f','7','54','644a378a85f48d3da0714079'),(207,'Rec005_Vox2.mrui--quest_param_117T_B.txt.tgz','532dc6e6a2b528a9f9fa091cc8f764c9','7','55','644a378a85f48d3da0714073'),(208,'Rec017_Vox1.mrui--quest_param_117T_B.txt.tgz','925f7afb9a13c4f6376670bd280a0bcb','7','56','644a378a85f48d3da071409d'),(209,'Rec005_Vox1.mrui--quest_param_117T_B.txt.tgz','1dccdb8ff331dc35513649a0c23cf9a6','7','57','644a378a85f48d3da0714071'),(210,'Rec019_Vox1.mrui--quest_param_117T_B.txt.tgz','089077bf7762050a2b5ab0a6332e9989','7','58','644a378b85f48d3da07140a5'),(211,'Rec010_Vox2.mrui--quest_param_117T_B.txt.tgz','38974803ac3109b89ad12c83f466b2b0','7','59','644a378a85f48d3da0714085'),(212,'Rec003_Vox2.mrui--quest_param_117T_B.txt.tgz','e9bfc7e9120fd0e264522e5ef51f6503','7','60','644a378a85f48d3da071406b'),(213,'Rec008_Vox1.mrui--quest_param_117T_B.txt.tgz','f9649794e6c25951a563d780e6b2c545','7','61','644a378a85f48d3da071407b'),(214,'Rec020_Vox2.mrui--quest_param_117T_B.txt.tgz','ba98987063fa0670c7ccdd09a8eba7d8','7','62','644a378b85f48d3da07140a9'),(215,'Rec010_Vox1.mrui--quest_param_117T_B.txt.tgz','fb88412f836b6f5fd4c8d03672723cac','7','63','644a378a85f48d3da0714083'),(216,'Rec018_Vox1.mrui--quest_param_117T_B.txt.tgz','e7df927eee195e68e6b5ff4d22f823b7','7','64','644a378b85f48d3da07140a1'),(217,'Rec011_Vox2.mrui--quest_param_117T_B.txt.tgz','084915f9d198c7256abb2cae00b85999','7','65','644a378a85f48d3da0714089'),(218,'Rec015_Vox2.mrui--quest_param_117T_B.txt.tgz','718a844257737d18842ab1150dba533e','7','66','644a378a85f48d3da0714097'),(219,'Rec011_Vox1.mrui--quest_param_117T_B.txt.tgz','0898b7d7ac28d6f423f36e766e6c3121','7','67','644a378a85f48d3da0714087'),(220,'Rec002_Vox1.mrui--quest_param_117T_B.txt.tgz','d82b35628c39a1eaefc84d723a2f6040','7','68','644a378a85f48d3da0714067'),(221,'Rec018_Vox2.mrui--quest_param_117T_B.txt.tgz','7d5f3f257e1cdc7183d9c8492ce5a056','7','69','644a378b85f48d3da07140a3'),(222,'Rec009_Vox1.mrui--quest_param_117T_B.txt.tgz','c35aec911b7c3699a22725286fcf5c88','7','70','644a378a85f48d3da071407f'),(223,'Rec014_Vox1.mrui--quest_param_117T_B.txt.tgz','5a841c35ff53a6cd1916aebc20d18204','7','71','644a378a85f48d3da0714091'),(224,'Rec001_Vox1.mrui--quest_param_117T_B.txt.tgz','10f0a14e6b779aa077b7a841c08b7cfe','7','72','644a378a85f48d3da0714063'),(225,'Rec016_Vox1.mrui--quest_param_117T_B.txt.tgz','93dae08ccc017528173dd8f32f3b9bf3','7','73','644a378a85f48d3da0714099'),(226,'Rec004_Vox1.mrui--quest_param_117T_B.txt.tgz','056a7e6d99217159dfc59a3a323d13b7','7','74','644a378a85f48d3da071406d'),(227,'Rec003_Vox1.mrui--quest_param_117T_B.txt.tgz','8db592065be83205eb6cd323910139d8','7','75','644a378a85f48d3da0714069'),(228,'Rec015_Vox1.mrui--quest_param_117T_B.txt.tgz','a1dfa4f6521308cfe1cc33fd37ae6607','7','76','644a378a85f48d3da0714095'),(229,'Rec001_Vox2.mrui--quest_param_117T_B.txt.tgz','49ea6063c9fc6de46b5a789ebeda0710','8','39','644a5cee85f48d3da0714838'),(230,'Rec012_Vox2.mrui--quest_param_117T_B.txt.tgz','7ab61cfcfbfec05f80216abe53297852','8','40','644a5cee85f48d3da0714860'),(231,'Rec012_Vox1.mrui--quest_param_117T_B.txt.tgz','6aafea0b2672ad441ae70236a098644d','8','41','644a5cee85f48d3da071485e'),(232,'Rec016_Vox2.mrui--quest_param_117T_B.txt.tgz','808aa2e0d7e0227d8b96d1e77c7477d2','8','42','644a5cee85f48d3da071486e'),(233,'Rec004_Vox2.mrui--quest_param_117T_B.txt.tgz','834418d5656cfef1c3d8054788489faa','8','43','644a5cee85f48d3da0714842'),(234,'Rec009_Vox2.mrui--quest_param_117T_B.txt.tgz','eb602258273724bdcbbbf9d3b21046f8','8','44','644a5cee85f48d3da0714854'),(235,'Rec007_Vox1.mrui--quest_param_117T_B.txt.tgz','3537a482471d80d024c15120b4477ded','8','45','644a5cee85f48d3da071484a'),(236,'Rec008_Vox2.mrui--quest_param_117T_B.txt.tgz','d4ca0b4346943fd429a786e45175d881','8','46','644a5cee85f48d3da0714850'),(237,'Rec014_Vox2.mrui--quest_param_117T_B.txt.tgz','46e07e19df186b722e89a25ec42f4f85','8','47','644a5cee85f48d3da0714866'),(238,'Rec013_Vox1.mrui--quest_param_117T_B.txt.tgz','7d7dac04ad8cfaedd26eaff40c36a3f3','8','48','644a5cee85f48d3da0714862'),(239,'Rec006_Vox1.mrui--quest_param_117T_B.txt.tgz','7c691d23b0f9aeeeb2da52e2119e2631','8','49','644a5cee85f48d3da0714848'),(240,'Rec017_Vox2.mrui--quest_param_117T_B.txt.tgz','898849cf5b4ed3ae11718f502690c1dc','8','50','644a5cef85f48d3da0714872'),(241,'Rec020_Vox1.mrui--quest_param_117T_B.txt.tgz','3c36b8c012a0831f9d24a1c74f3b946b','8','51','644a5cef85f48d3da071487a'),(242,'Rec021_Vox1.mrui--quest_param_117T_B.txt.tgz','5a9ff1ad7e29484ad1c0cd95f8786572','8','52','644a5cef85f48d3da071487e'),(243,'Rec021_Vox2.mrui--quest_param_117T_B.txt.tgz','faab100e423e64ad05caefd847bd900a','8','53','644a5cef85f48d3da0714880'),(244,'Rec007_Vox2.mrui--quest_param_117T_B.txt.tgz','f962483acd27e2587c1679de4c478ad8','8','54','644a5cee85f48d3da071484c'),(245,'Rec005_Vox2.mrui--quest_param_117T_B.txt.tgz','774e2c9441b6515201c9c3047825f48b','8','55','644a5cee85f48d3da0714846'),(246,'Rec017_Vox1.mrui--quest_param_117T_B.txt.tgz','b7a928f978bcecdbec20575c12e2859e','8','56','644a5cef85f48d3da0714870'),(247,'Rec005_Vox1.mrui--quest_param_117T_B.txt.tgz','903bfdfd1fd7142af7ee9d64792ecbb7','8','57','644a5cee85f48d3da0714844'),(248,'Rec019_Vox1.mrui--quest_param_117T_B.txt.tgz','4f4c08512dc8b7eed1c4f59c3e4b268f','8','58','644a5cef85f48d3da0714878'),(249,'Rec010_Vox2.mrui--quest_param_117T_B.txt.tgz','23045da43649c522369187b0ab617fcf','8','59','644a5cee85f48d3da0714858'),(250,'Rec003_Vox2.mrui--quest_param_117T_B.txt.tgz','b5ef695c277fffd611265e65f3b9da21','8','60','644a5cee85f48d3da071483e'),(251,'Rec008_Vox1.mrui--quest_param_117T_B.txt.tgz','c5ff131d391de7bcceb2c7ef7c62f236','8','61','644a5cee85f48d3da071484e'),(252,'Rec020_Vox2.mrui--quest_param_117T_B.txt.tgz','843371cfd528f8f1127bfa24c7f198a0','8','62','644a5cef85f48d3da071487c'),(253,'Rec010_Vox1.mrui--quest_param_117T_B.txt.tgz','2a39934b936126f87b84e9d58465db25','8','63','644a5cee85f48d3da0714856'),(254,'Rec018_Vox1.mrui--quest_param_117T_B.txt.tgz','c2beb5a84ba5646d682e8b38fddc7637','8','64','644a5cef85f48d3da0714874'),(255,'Rec011_Vox2.mrui--quest_param_117T_B.txt.tgz','ea39545f83eb558bae4f1a27ef8a28b4','8','65','644a5cee85f48d3da071485c'),(256,'Rec015_Vox2.mrui--quest_param_117T_B.txt.tgz','ed55539a5f84e063361385998ec2c60c','8','66','644a5cee85f48d3da071486a'),(257,'Rec011_Vox1.mrui--quest_param_117T_B.txt.tgz','60f84a502791b93ba1498768f82f8391','8','67','644a5cee85f48d3da071485a'),(258,'Rec002_Vox1.mrui--quest_param_117T_B.txt.tgz','96871684f3fed2f60360c8052c63a807','8','68','644a5cee85f48d3da071483a'),(259,'Rec018_Vox2.mrui--quest_param_117T_B.txt.tgz','9da1be7915a076f044929753278ed7cd','8','69','644a5cef85f48d3da0714876'),(260,'Rec009_Vox1.mrui--quest_param_117T_B.txt.tgz','48323bdfd2aa0c0b9870a15aea3a93d5','8','70','644a5cee85f48d3da0714852'),(261,'Rec014_Vox1.mrui--quest_param_117T_B.txt.tgz','a74337a3d11cff065a76b211d62f7640','8','71','644a5cee85f48d3da0714864'),(262,'Rec001_Vox1.mrui--quest_param_117T_B.txt.tgz','b2e1ae27a07554897a09545e005092f1','8','72','644a5cee85f48d3da0714836'),(263,'Rec016_Vox1.mrui--quest_param_117T_B.txt.tgz','c72ad229025cdf05428adf7a9e8b247c','8','73','644a5cee85f48d3da071486c'),(264,'Rec004_Vox1.mrui--quest_param_117T_B.txt.tgz','9e1c7549a6dc320c6d0ea7bc6b4ce558','8','74','644a5cee85f48d3da0714840'),(265,'Rec003_Vox1.mrui--quest_param_117T_B.txt.tgz','15e9b8c2698016e8616a56a0b8276ab9','8','75','644a5cee85f48d3da071483c'),(266,'Rec015_Vox1.mrui--quest_param_117T_B.txt.tgz','3d17cb75d27797718178ddf897f5da71','8','76','644a5cee85f48d3da0714868'),(267,'Rec001_Vox2.mrui--quest_param_117T_B.txt.tgz','458def972c725d39f1695e38f27159e6','9','39','644a274085f48d3da0713df4'),(268,'Rec012_Vox2.mrui--quest_param_117T_B.txt.tgz','80b0fb7f2ccdeb2799c9c079f9774d59','9','40','644a274185f48d3da0713e1c'),(269,'Rec012_Vox1.mrui--quest_param_117T_B.txt.tgz','60ececb6836de506aa70a919cc66d5a6','9','41','644a274185f48d3da0713e1a'),(270,'Rec016_Vox2.mrui--quest_param_117T_B.txt.tgz','dc79033d85f149b80f4083b4cd19b63d','9','42','644a274185f48d3da0713e2a'),(271,'Rec004_Vox2.mrui--quest_param_117T_B.txt.tgz','14f2b5f3e868ea3886275bc53ff3f0dd','9','43','644a274085f48d3da0713dfe'),(272,'Rec009_Vox2.mrui--quest_param_117T_B.txt.tgz','0ff4cc7f793e4cc325cc857cc3a5f6e8','9','44','644a274185f48d3da0713e10'),(273,'Rec007_Vox1.mrui--quest_param_117T_B.txt.tgz','dbc13dd761c56ccc86916d399ffbcfb4','9','45','644a274085f48d3da0713e06'),(274,'Rec008_Vox2.mrui--quest_param_117T_B.txt.tgz','2e7215c78294ad601008d933f3bb7c0c','9','46','644a274185f48d3da0713e0c'),(275,'Rec014_Vox2.mrui--quest_param_117T_B.txt.tgz','e6bfb82e820f9b08cf282970066cedca','9','47','644a274185f48d3da0713e22'),(276,'Rec013_Vox1.mrui--quest_param_117T_B.txt.tgz','8a6e9bd0499d641277160d4251db3e42','9','48','644a274185f48d3da0713e1e'),(277,'Rec006_Vox1.mrui--quest_param_117T_B.txt.tgz','7973ede85b3e0326cf0a71ef0a385eeb','9','49','644a274085f48d3da0713e04'),(278,'Rec017_Vox2.mrui--quest_param_117T_B.txt.tgz','8f290bf37bde1e7d2b99174e6819b9b1','9','50','644a274185f48d3da0713e2e'),(279,'Rec020_Vox1.mrui--quest_param_117T_B.txt.tgz','ced663ba659a80e1b7453cc9126f7fe7','9','51','644a274185f48d3da0713e36'),(280,'Rec021_Vox1.mrui--quest_param_117T_B.txt.tgz','5b724bf24d8216ce6b5c924ce50e6f5e','9','52','644a274185f48d3da0713e3a'),(281,'Rec021_Vox2.mrui--quest_param_117T_B.txt.tgz','05398db14e992c79341cb6ca97c24b02','9','53','644a274185f48d3da0713e3c'),(282,'Rec007_Vox2.mrui--quest_param_117T_B.txt.tgz','6c0e13e26123becd5e63743908c1d772','9','54','644a274085f48d3da0713e08'),(283,'Rec005_Vox2.mrui--quest_param_117T_B.txt.tgz','3445d7160cb38f23e03f520aad85f8c5','9','55','644a274085f48d3da0713e02'),(284,'Rec017_Vox1.mrui--quest_param_117T_B.txt.tgz','01182c6eef463fe8943df9e524659cf5','9','56','644a274185f48d3da0713e2c'),(285,'Rec005_Vox1.mrui--quest_param_117T_B.txt.tgz','61a079401e2030c23b5909a787be8845','9','57','644a274085f48d3da0713e00'),(286,'Rec019_Vox1.mrui--quest_param_117T_B.txt.tgz','66ed6b3ccfcb18fef3a9f846a87c5a79','9','58','644a274185f48d3da0713e34'),(287,'Rec010_Vox2.mrui--quest_param_117T_B.txt.tgz','177c68e0ccf6c39b200f4946823b06f1','9','59','644a274185f48d3da0713e14'),(288,'Rec003_Vox2.mrui--quest_param_117T_B.txt.tgz','dd17869262492a5d9cf67f78b9351e0f','9','60','644a274085f48d3da0713dfa'),(289,'Rec008_Vox1.mrui--quest_param_117T_B.txt.tgz','aaf44ddaeef584958c1921b98b40062f','9','61','644a274085f48d3da0713e0a'),(290,'Rec020_Vox2.mrui--quest_param_117T_B.txt.tgz','eab80ad606b37cd617850634b6d0e91b','9','62','644a274185f48d3da0713e38'),(291,'Rec010_Vox1.mrui--quest_param_117T_B.txt.tgz','2f7c1ebfcb5e482230ac8a2983cc0a98','9','63','644a274185f48d3da0713e12'),(292,'Rec018_Vox1.mrui--quest_param_117T_B.txt.tgz','693416a53609e92439a78be3a6c10f3d','9','64','644a274185f48d3da0713e30'),(293,'Rec011_Vox2.mrui--quest_param_117T_B.txt.tgz','efb2f2275628acc19a89ff558773389b','9','65','644a274185f48d3da0713e18'),(294,'Rec015_Vox2.mrui--quest_param_117T_B.txt.tgz','6e77a7cea8eac032f1b2c9191de3bd49','9','66','644a274185f48d3da0713e26'),(295,'Rec011_Vox1.mrui--quest_param_117T_B.txt.tgz','a4afb76694b8991e889493b70831ca18','9','67','644a274185f48d3da0713e16'),(296,'Rec002_Vox1.mrui--quest_param_117T_B.txt.tgz','40e8be47f042410a6e385e571d2cb443','9','68','644a274085f48d3da0713df6'),(297,'Rec018_Vox2.mrui--quest_param_117T_B.txt.tgz','c2934faefcadedce0c5bb0e2aa6efca4','9','69','644a274185f48d3da0713e32'),(298,'Rec009_Vox1.mrui--quest_param_117T_B.txt.tgz','bc9fc7c315c2ed93c66cba671ebb1b5c','9','70','644a274185f48d3da0713e0e'),(299,'Rec014_Vox1.mrui--quest_param_117T_B.txt.tgz','3e828f94acb4226ba33e09782576b2c1','9','71','644a274185f48d3da0713e20'),(300,'Rec001_Vox1.mrui--quest_param_117T_B.txt.tgz','798fbfac4f6966d65cb10108227afaf6','9','72','644a274085f48d3da0713df2'),(301,'Rec016_Vox1.mrui--quest_param_117T_B.txt.tgz','d41a4f8bda7bd9979d48fe75909d08ec','9','73','644a274185f48d3da0713e28'),(302,'Rec004_Vox1.mrui--quest_param_117T_B.txt.tgz','9c8b2c8f9fa547cf569258446f63d1f0','9','74','644a274085f48d3da0713dfc'),(303,'Rec003_Vox1.mrui--quest_param_117T_B.txt.tgz','04ebb288a7dc6078e1638665cefa978e','9','75','644a274085f48d3da0713df8'),(304,'Rec015_Vox1.mrui--quest_param_117T_B.txt.tgz','23968c2e9c7a9d5e1485b2aa1a64494a','9','76','644a274185f48d3da0713e24'),(305,'Rec001_Vox2.mrui--quest_param_117T_B.txt.tgz','3a8e9d2dc80ede6cc489650c8b028103','10','39','644a415985f48d3da0714316'),(306,'Rec012_Vox2.mrui--quest_param_117T_B.txt.tgz','5ff9299473920b1475b5d8773644651e','10','40','644a415a85f48d3da071433e'),(307,'Rec012_Vox1.mrui--quest_param_117T_B.txt.tgz','fe53a3f99f9b45d393cfbf5a4d7a2cd7','10','41','644a415a85f48d3da071433c'),(308,'Rec016_Vox2.mrui--quest_param_117T_B.txt.tgz','34d6c70f7e9cf52838021d410ac1072a','10','42','644a415a85f48d3da071434c'),(309,'Rec004_Vox2.mrui--quest_param_117T_B.txt.tgz','d048c324f43bcf1b2edf5f49dff7512a','10','43','644a415985f48d3da0714320'),(310,'Rec009_Vox2.mrui--quest_param_117T_B.txt.tgz','1597281780e0261409b053b7b6a39bd3','10','44','644a415985f48d3da0714332'),(311,'Rec007_Vox1.mrui--quest_param_117T_B.txt.tgz','36a00ce4ee327be9c463202206dd0e2e','10','45','644a415985f48d3da0714328'),(312,'Rec008_Vox2.mrui--quest_param_117T_B.txt.tgz','5c235e80191eccb03902c764949e7a00','10','46','644a415985f48d3da071432e'),(313,'Rec014_Vox2.mrui--quest_param_117T_B.txt.tgz','c26432e25d78d99f9e84b11fe642cad7','10','47','644a415a85f48d3da0714344'),(314,'Rec013_Vox1.mrui--quest_param_117T_B.txt.tgz','36500d6aba2857e89fb7f622c74e7134','10','48','644a415a85f48d3da0714340'),(315,'Rec006_Vox1.mrui--quest_param_117T_B.txt.tgz','9e0df509f086ca888c99185cadffa723','10','49','644a415985f48d3da0714326'),(316,'Rec017_Vox2.mrui--quest_param_117T_B.txt.tgz','dde9fa684cf83cb4abbb081dfc820a40','10','50','644a415a85f48d3da0714350'),(317,'Rec020_Vox1.mrui--quest_param_117T_B.txt.tgz','29fea853b241fc99d6300cf22addb03c','10','51','644a415a85f48d3da0714358'),(318,'Rec021_Vox1.mrui--quest_param_117T_B.txt.tgz','e2252af7cc34aaf483f33e20d850db67','10','52','644a415a85f48d3da071435c'),(319,'Rec021_Vox2.mrui--quest_param_117T_B.txt.tgz','b533dfda3ed6286afb588c51f1be0080','10','53','644a415a85f48d3da071435e'),(320,'Rec007_Vox2.mrui--quest_param_117T_B.txt.tgz','8b79416d438197fd8be491bd6eb2e665','10','54','644a415985f48d3da071432a'),(321,'Rec005_Vox2.mrui--quest_param_117T_B.txt.tgz','ac54e795f005923ef1d34f3321a0b249','10','55','644a415985f48d3da0714324'),(322,'Rec017_Vox1.mrui--quest_param_117T_B.txt.tgz','ebae4ea2857a3108e80430a389117760','10','56','644a415a85f48d3da071434e'),(323,'Rec005_Vox1.mrui--quest_param_117T_B.txt.tgz','55306da7ffefaff6916430b60c56b275','10','57','644a415985f48d3da0714322'),(324,'Rec019_Vox1.mrui--quest_param_117T_B.txt.tgz','e2ea92bcf131e407eeb25b51f86e99b1','10','58','644a415a85f48d3da0714356'),(325,'Rec010_Vox2.mrui--quest_param_117T_B.txt.tgz','c24ebd33d76dddee031659d1ee713529','10','59','644a415985f48d3da0714336'),(326,'Rec003_Vox2.mrui--quest_param_117T_B.txt.tgz','238d1c1e463528bce88027aa2a841358','10','60','644a415985f48d3da071431c'),(327,'Rec008_Vox1.mrui--quest_param_117T_B.txt.tgz','900702524ffe0c36545081fa568e8c9f','10','61','644a415985f48d3da071432c'),(328,'Rec020_Vox2.mrui--quest_param_117T_B.txt.tgz','2f6d1c7f25b39e47954143c95d5d5e5f','10','62','644a415a85f48d3da071435a'),(329,'Rec010_Vox1.mrui--quest_param_117T_B.txt.tgz','15c2d465aacd9c909f7bfecdcb955930','10','63','644a415985f48d3da0714334'),(330,'Rec018_Vox1.mrui--quest_param_117T_B.txt.tgz','a392f0e8e4d029de5d667603d74672ab','10','64','644a415a85f48d3da0714352'),(331,'Rec011_Vox2.mrui--quest_param_117T_B.txt.tgz','a5b383ad5f37901507a5f39ec1aa8e0f','10','65','644a415985f48d3da071433a'),(332,'Rec015_Vox2.mrui--quest_param_117T_B.txt.tgz','d5816e2ce93fedad7faaf57d62149d51','10','66','644a415a85f48d3da0714348'),(333,'Rec011_Vox1.mrui--quest_param_117T_B.txt.tgz','a5d0adf69e70881e218d10e83cb404a6','10','67','644a415985f48d3da0714338'),(334,'Rec002_Vox1.mrui--quest_param_117T_B.txt.tgz','d9f6069a32127b1da11a3c2577edb4cb','10','68','644a415985f48d3da0714318'),(335,'Rec018_Vox2.mrui--quest_param_117T_B.txt.tgz','1eeb4dbc42020bef188ba540114aecc4','10','69','644a415a85f48d3da0714354'),(336,'Rec009_Vox1.mrui--quest_param_117T_B.txt.tgz','f10840aef93219b9517b3528ddf97fdf','10','70','644a415985f48d3da0714330'),(337,'Rec014_Vox1.mrui--quest_param_117T_B.txt.tgz','e6144d5937f4ce23de6df1f2f9f08e52','10','71','644a415a85f48d3da0714342'),(338,'Rec001_Vox1.mrui--quest_param_117T_B.txt.tgz','53cd3c85fdd81ca02ea3a0533831d40f','10','72','644a415985f48d3da0714314'),(339,'Rec016_Vox1.mrui--quest_param_117T_B.txt.tgz','9e5338e057c5822f2d9f3dc23b3c3999','10','73','644a415a85f48d3da071434a'),(340,'Rec004_Vox1.mrui--quest_param_117T_B.txt.tgz','d944c53603aa99efe98c44d9533faa4c','10','74','644a415985f48d3da071431e'),(341,'Rec003_Vox1.mrui--quest_param_117T_B.txt.tgz','961ff37c3047f511227343c52a2c6d0b','10','75','644a415985f48d3da071431a'),(342,'Rec015_Vox1.mrui--quest_param_117T_B.txt.tgz','980f38de9afad2da6868d6af22506a3d','10','76','644a415a85f48d3da0714346'),(343,'Rec001_Vox2.mrui--quest_param_117T_B.txt.tgz','6b8e0a101ef5db371c93c6d346eae6d8','11','39','644a453785f48d3da07145e9'),(344,'Rec012_Vox2.mrui--quest_param_117T_B.txt.tgz','9ff62047b8cf753d1c131725cc173829','11','40','644a453885f48d3da0714611'),(345,'Rec012_Vox1.mrui--quest_param_117T_B.txt.tgz','19c45a3421b784cc6260f65a19bc9aeb','11','41','644a453885f48d3da071460f'),(346,'Rec016_Vox2.mrui--quest_param_117T_B.txt.tgz','26010bff23c970aac8e7f61229494401','11','42','644a453885f48d3da071461f'),(347,'Rec004_Vox2.mrui--quest_param_117T_B.txt.tgz','2d6304fff995ec1c826761631e24ff83','11','43','644a453785f48d3da07145f3'),(348,'Rec009_Vox2.mrui--quest_param_117T_B.txt.tgz','f478b44bf54b5caad2a70fcabc77418b','11','44','644a453785f48d3da0714605'),(349,'Rec007_Vox1.mrui--quest_param_117T_B.txt.tgz','7cc4617dc4e2ebebef7c470a5b3cbdea','11','45','644a453785f48d3da07145fb'),(350,'Rec008_Vox2.mrui--quest_param_117T_B.txt.tgz','17d4b5239b17d515e1bea9e1a11eed2b','11','46','644a453785f48d3da0714601'),(351,'Rec014_Vox2.mrui--quest_param_117T_B.txt.tgz','ba08888ff73882b29289c2f8f3650196','11','47','644a453885f48d3da0714617'),(352,'Rec013_Vox1.mrui--quest_param_117T_B.txt.tgz','29e151d30757133670b8628b200e0600','11','48','644a453885f48d3da0714613'),(353,'Rec006_Vox1.mrui--quest_param_117T_B.txt.tgz','ea893b78b2e37b538fc08729c0b897fe','11','49','644a453785f48d3da07145f9'),(354,'Rec017_Vox2.mrui--quest_param_117T_B.txt.tgz','dc8fff11a74d380bb2e595740a9d5dae','11','50','644a453885f48d3da0714623'),(355,'Rec020_Vox1.mrui--quest_param_117T_B.txt.tgz','2a5b586677a5b2f0765083d017f52df1','11','51','644a453885f48d3da071462b'),(356,'Rec021_Vox1.mrui--quest_param_117T_B.txt.tgz','0f0cc35564225eb52f492d9eb4b48bf4','11','52','644a453885f48d3da071462f'),(357,'Rec021_Vox2.mrui--quest_param_117T_B.txt.tgz','53b1f4cbb5a47bd6d4aca9ab166071b4','11','53','644a453885f48d3da0714631'),(358,'Rec007_Vox2.mrui--quest_param_117T_B.txt.tgz','090127e1c387536199ebe7abfdd50509','11','54','644a453785f48d3da07145fd'),(359,'Rec005_Vox2.mrui--quest_param_117T_B.txt.tgz','ef649e28fd467f58f66b41d910ee5b25','11','55','644a453785f48d3da07145f7'),(360,'Rec017_Vox1.mrui--quest_param_117T_B.txt.tgz','e2fe1e0b839cc6bad8c65cb5e9d2717f','11','56','644a453885f48d3da0714621'),(361,'Rec005_Vox1.mrui--quest_param_117T_B.txt.tgz','4ebb106b82e9c392e8064311d748d993','11','57','644a453785f48d3da07145f5'),(362,'Rec019_Vox1.mrui--quest_param_117T_B.txt.tgz','b78b7b3e8ce1c4595f8463e47f7fcea3','11','58','644a453885f48d3da0714629'),(363,'Rec010_Vox2.mrui--quest_param_117T_B.txt.tgz','00bbc422c4b6d2ec3bc3b0956794600d','11','59','644a453785f48d3da0714609'),(364,'Rec003_Vox2.mrui--quest_param_117T_B.txt.tgz','38658c43017da56441c12e6d69df17ff','11','60','644a453785f48d3da07145ef'),(365,'Rec008_Vox1.mrui--quest_param_117T_B.txt.tgz','7de34a262810293e457a738a18b7fbf2','11','61','644a453785f48d3da07145ff'),(366,'Rec020_Vox2.mrui--quest_param_117T_B.txt.tgz','5dc35d97126469cd325df8b389eeb9db','11','62','644a453885f48d3da071462d'),(367,'Rec010_Vox1.mrui--quest_param_117T_B.txt.tgz','d5d88aae2dd3af82ef4dbe74e43b08c5','11','63','644a453785f48d3da0714607'),(368,'Rec018_Vox1.mrui--quest_param_117T_B.txt.tgz','97f84a4fd80f97c0da1a361b51e50aa5','11','64','644a453885f48d3da0714625'),(369,'Rec011_Vox2.mrui--quest_param_117T_B.txt.tgz','2b9693e3dac1197e8c1e014a4da0ad61','11','65','644a453785f48d3da071460d'),(370,'Rec015_Vox2.mrui--quest_param_117T_B.txt.tgz','e245c831cbda7ceabaac8e48f5775074','11','66','644a453885f48d3da071461b'),(371,'Rec011_Vox1.mrui--quest_param_117T_B.txt.tgz','2991ad450e306e06eaf937c673fc5a3e','11','67','644a453785f48d3da071460b'),(372,'Rec002_Vox1.mrui--quest_param_117T_B.txt.tgz','1a967eb06715cf47a98b22492f3d4d1c','11','68','644a453785f48d3da07145eb'),(373,'Rec018_Vox2.mrui--quest_param_117T_B.txt.tgz','28c4c5f7da7492855fe2b1369697191f','11','69','644a453885f48d3da0714627'),(374,'Rec009_Vox1.mrui--quest_param_117T_B.txt.tgz','f2d7164d8ab8da2dbdfe2e6f5bc54459','11','70','644a453785f48d3da0714603'),(375,'Rec014_Vox1.mrui--quest_param_117T_B.txt.tgz','5628f304be802a3abfe675cfa97c3284','11','71','644a453885f48d3da0714615'),(376,'Rec001_Vox1.mrui--quest_param_117T_B.txt.tgz','b1496eb064786bc4ab920b99be842766','11','72','644a453785f48d3da07145e7'),(377,'Rec016_Vox1.mrui--quest_param_117T_B.txt.tgz','1c98c4f6f4f91597c334bd8ca2c0f304','11','73','644a453885f48d3da071461d'),(378,'Rec004_Vox1.mrui--quest_param_117T_B.txt.tgz','cdd3bb09d37f3ca14a75f36131ec72b9','11','74','644a453785f48d3da07145f1'),(379,'Rec003_Vox1.mrui--quest_param_117T_B.txt.tgz','886aef70850a6ff942c630bd286a70f2','11','75','644a453785f48d3da07145ed'),(380,'Rec015_Vox1.mrui--quest_param_117T_B.txt.tgz','d1ae73bc5d70d5ec86ac869b321c1bb6','11','76','644a453885f48d3da0714619'),(384,'UPENN-GBM-00019','798fbfac4f6966d65cb10108227afaf7','14','80','646f415585f48d3da071909f');
/*!40000 ALTER TABLE `output` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `parameter`
--

DROP TABLE IF EXISTS `parameter`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `parameter` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(45) NOT NULL,
  `md5` varchar(45) NOT NULL,
  `girder_id` varchar(45) NOT NULL,
  `value` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `parameter`
--

LOCK TABLES `parameter` WRITE;
/*!40000 ALTER TABLE `parameter` DISABLE KEYS */;
INSERT INTO `parameter` VALUES (2,'quest_param_117T_B.txt','4480fe6387d7103d356d4a9bb00d6cd7','63e0d46c0386da2747642010',NULL);
/*!40000 ALTER TABLE `parameter` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `username` varchar(45) NOT NULL,
  `password` varchar(256) NOT NULL,
  `role` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (1,'Hippo','$2b$12$HdEIckmjB32/g8wtvWg4hORd4ZQJpM2Dq2FPTCivGhMoN.aB7rb9K','admin');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `workflow`
--

DROP TABLE IF EXISTS `workflow`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `workflow` (
  `id` int NOT NULL AUTO_INCREMENT,
  `timestamp` varchar(45) NOT NULL,
  `experiment_id` varchar(45) NOT NULL,
  `girder_id` varchar(45) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `workflow`
--

LOCK TABLES `workflow` WRITE;
/*!40000 ALTER TABLE `workflow` DISABLE KEYS */;
INSERT INTO `workflow` VALUES (7,'2023-03-16_17:26:37','5','644a378a85f48d3da0714061'),(8,'2023-03-16_17:07:38','6','644a5cee85f48d3da0714834'),(9,'2023-03-16_16:34:46','7','644a274085f48d3da0713df0'),(10,'2023-03-16_16:34:54','7','644a415985f48d3da0714312'),(11,'2023-03-17_15:02:01','8','644a453785f48d3da07145e5'),(14,'1','10','646c7cd885f48d3da0718d4a');
/*!40000 ALTER TABLE `workflow` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2023-06-29 10:58:22
