drop table access_area;
drop table antenna;
drop table antenna_pattern;
drop table antenna_polarity;
drop table applic_text_block;
drop table auth_spectrum_area;
drop table auth_spectrum_freq;
drop table bsl;
drop table bsl_area;
drop table class_of_station;
drop table client;
drop table client_type;
drop table device_details;
drop table fee_status;
drop table industry_cat;
drop table licence;
drop table licence_service;
drop table licence_status;
drop table licence_subservice;
drop table licensing_area;
drop table nature_of_service;
drop table reports_text_block;
drop table satellite;
drop table site;


create table access_area(
 AREA_ID		NUMBER(10),
 AREA_CODE              VARCHAR2(256),
 AREA_NAME              VARCHAR2(256),
 AREA_CATEGORY          NUMBER);

create table antenna(
 ANTENNA_ID		VARCHAR2(31),
 GAIN                   NUMBER,
 FRONT_TO_BACK          NUMBER,
 H_BEAMWIDTH            NUMBER,
 V_BEAMWIDTH            NUMBER,
 BAND_MIN_FREQ          NUMBER,
 BAND_MIN_FREQ_UNIT     VARCHAR2(3),
 BAND_MAX_FREQ          NUMBER,
 BAND_MAX_FREQ_UNIT     VARCHAR2(3),
 ANTENNA_SIZE           NUMBER,
 ANTENNA_TYPE           VARCHAR2(240),
 MODEL                  VARCHAR2(80),
 MANUFACTURER           VARCHAR2(255));

create table antenna_pattern(
 ANTENNA_ID		VARCHAR2(31),
 AZ_TYPE                VARCHAR2(15),
 ANGLE_REF              NUMBER,
 ANGLE                  NUMBER,
 ATTENUATION            NUMBER);

create table antenna_polarity(
 POLARISATION_CODE	VARCHAR2(3),
 POLARISATION_TEXT      VARCHAR2(50));

create table applic_text_block(
 APTB_ID		NUMBER,
 APTB_TABLE_PREFIX	VARCHAR2(30),
 APTB_TABLE_ID          NUMBER(10),
 LICENCE_NO             VARCHAR2(63),
 APTB_DESCRIPTION       VARCHAR2(255),
 APTB_CATEGORY          VARCHAR2(255),
 APTB_TEXT              VARCHAR2(4000),
 APTB_ITEM              VARCHAR2(15));

create table auth_spectrum_area(
 LICENCE_NO  		VARCHAR2(63),
 AREA_CODE              VARCHAR2(256),
 AREA_NAME              VARCHAR2(256),
 AREA_DESCRIPTION       CLOB);

create table auth_spectrum_freq(
 LICENCE_NO		VARCHAR2(63),
 AREA_CODE              VARCHAR2(256),
 AREA_NAME              VARCHAR2(256),
 LW_FREQUENCY_START     NUMBER,
 LW_FREQUENCY_END       NUMBER,
 UP_FREQUENCY_START     NUMBER,
 UP_FREQUENCY_END       NUMBER);

create table bsl(
 BSL_NO                 VARCHAR2(31),
 MEDIUM_CATEGORY        VARCHAR2(4000),
 REGION_CATEGORY        VARCHAR2(4000),
 COMMUNITY_INTEREST     VARCHAR2(4000),
 BSL_STATE              VARCHAR2(4000),
 DATE_COMMENCED         DATE,
 ON_AIR_ID              VARCHAR2(511),
 CALL_SIGN              VARCHAR2(255),
 IBL_TARGET_AREA        VARCHAR2(511),
 AREA_CODE              VARCHAR2(256),
 REFERENCE              VARCHAR2(63)
);

create table bsl_area(
 AREA_CODE		VARCHAR2(256),
 AREA_NAME		VARCHAR2(256)
);

create table class_of_station(
 CODE			VARCHAR2(31),
 DESCRIPTION            VARCHAR2(511));

create table client(
 CLIENT_NO		NUMBER,
 LICENCEE               VARCHAR2(201),
 TRADING_NAME           VARCHAR2(100),
 ACN                    VARCHAR2(100),
 ABN                    VARCHAR2(14),
 POSTAL_STREET          VARCHAR2(600),
 POSTAL_SUBURB          VARCHAR2(480),
 POSTAL_STATE           VARCHAR2(36),
 POSTAL_POSTCODE        VARCHAR2(72),
 CAT_ID                 NUMBER,
 CLIENT_TYPE_ID         NUMBER,
 FEE_STATUS_ID          NUMBER);

create table client_type(
 TYPE_ID		NUMBER,
 NAME                   VARCHAR2(240));

create table device_details(
 SDD_ID   				NUMBER(10),
 LICENCE_NO                             VARCHAR2(63),
 DEVICE_REGISTRATION_IDENTIFIER         VARCHAR2(63),
 FORMER_DEVICE_IDENTIFIER               VARCHAR2(63),
 AUTHORISATION_DATE                     DATE,
 CERTIFICATION_METHOD                   VARCHAR2(255),
 GROUP_FLAG                             VARCHAR2(255),
 SITE_RADIUS                            NUMBER,
 FREQUENCY                              NUMBER,
 BANDWIDTH                              NUMBER,
 CARRIER_FREQ                           NUMBER,
 EMISSION                               VARCHAR2(63),
 DEVICE_TYPE                            VARCHAR2(1),
 TRANSMITTER_POWER                      NUMBER,
 TRANSMITTER_POWER_UNIT                 VARCHAR2(31),
 SITE_ID                                VARCHAR2(31),
 ANTENNA_ID                             VARCHAR2(31),
 POLARISATION                           VARCHAR2(3),
 AZIMUTH                                NUMBER,
 HEIGHT                                 NUMBER,
 TILT                                   NUMBER,
 FEEDER_LOSS                            NUMBER,
 LEVEL_OF_PROTECTION                    NUMBER,
 EIRP                                   NUMBER,
 EIRP_UNIT                              VARCHAR2(31),
 SV_ID                                  NUMBER(10),
 SS_ID                                  NUMBER(10),
 EFL_ID                                 VARCHAR2(40),
 EFL_FREQ_IDENT                         VARCHAR2(31),
 EFL_SYSTEM                             VARCHAR2(63),
 LEQD_MODE                              VARCHAR2(1),
 RECEIVER_THRESHOLD                     NUMBER,
 AREA_AREA_ID                           NUMBER(10),
 CALL_SIGN                              VARCHAR2(255),
 AREA_DESCRIPTION                       VARCHAR2(9),
 AP_ID                                  NUMBER(10),
 CLASS_OF_STATION_CODE                  VARCHAR2(31),
 SUPPLIMENTAL_FLAG                      VARCHAR2(199),
 EQ_FREQ_RANGE_MIN                      NUMBER,
 EQ_FREQ_RANGE_MAX                      NUMBER,
 NATURE_OF_SERVICE_ID                   VARCHAR2(3),
 HOURS_OF_OPERATION                     VARCHAR2(11),
 SA_ID                                  NUMBER(10),
 RELATED_EFL_ID                         NUMBER,
 EQP_ID                                 NUMBER(10),
 ANTENNA_MULTI_MODE                     VARCHAR2(3),
 POWER_IND                              VARCHAR2(14),
 LPON_CENTER_LONGITUDE                  NUMBER,
 LPON_CENTER_LATITUDE                   NUMBER,
 TCS_ID                                 NUMBER(10),
 TECH_SPEC_ID                           VARCHAR2(63),
 DROPTHROUGH_ID                         VARCHAR2(63),
 STATION_TYPE                           VARCHAR2(511),
 STATION_NAME                           VARCHAR2(63));

create table fee_status(
 FEE_STATUS_ID		NUMBER,
 FEE_STATUS_TEXT        VARCHAR2(100));

create table industry_cat(
 CAT_ID			NUMBER,
 DESCRIPTION            VARCHAR2(240),
 NAME                   VARCHAR2(120));

create table licence(
 LICENCE_NO		VARCHAR2(63),
 CLIENT_NO              NUMBER,
 SV_ID                  NUMBER(10),
 SS_ID                  NUMBER(10),
 LICENCE_TYPE_NAME      VARCHAR2(63),
 LICENCE_CATEGORY_NAME  VARCHAR2(95),
 DATE_ISSUED            DATE,
 DATE_OF_EFFECT         DATE,
 DATE_OF_EXPIRY         DATE,
 STATUS                 VARCHAR2(10),
 STATUS_TEXT            VARCHAR2(256),
 AP_ID                  NUMBER(10),
 AP_PRJ_IDENT           VARCHAR2(511),
 SHIP_NAME              VARCHAR2(255),
 BSL_NO                 VARCHAR2(31)
 AWL_TYPE               VARCHAR2(511));

create table licence_service(
 SV_ID			NUMBER(10),
 SV_NAME                VARCHAR2(63));

create table licence_status(
 STATUS			VARCHAR2(10),
 STATUS_TEXT            VARCHAR2(511));

create table licence_subservice(
 SS_ID			NUMBER(10),
 SV_SV_ID               NUMBER(10),
 SS_NAME                VARCHAR2(95));

create table licensing_area(
 LICENSING_AREA_ID	VARCHAR2(31),
 DESCRIPTION            VARCHAR2(511));

create table nature_of_service(
 CODE			VARCHAR2(31),
 DESCRIPTION            VARCHAR2(511));

create table reports_text_block(
 RTB_ITEM		VARCHAR2(15),
 RTB_CATEGORY           VARCHAR2(255),
 RTB_DESCRIPTION        VARCHAR2(255),
 RTB_START_DATE         DATE,
 RTB_END_DATE           DATE,
 RTB_TEXT               VARCHAR2(4000));

create table satellite(
 SA_ID			NUMBER(10),
 SA_SAT_NAME            VARCHAR2(31),
 SA_SAT_LONG_NOM        NUMBER,
 SA_SAT_INCEXC          NUMBER,
 SA_SAT_GEO_POS         VARCHAR2(1),
 SA_SAT_MERIT_G_T       NUMBER);

create table site(
 SITE_ID		VARCHAR2(31),
 LATITUDE               NUMBER,
 LONGITUDE              NUMBER,
 NAME                   VARCHAR2(767),
 STATE                  VARCHAR2(80),
 LICENSING_AREA_ID      NUMBER,
 POSTCODE               VARCHAR2(18),
 SITE_PRECISION         VARCHAR2(31),
 ELEVATION              NUMBER,
 HCIS_L2		VARCHAR2(31));

