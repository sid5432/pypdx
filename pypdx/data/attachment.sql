create table if not exists attachment (
   "itemuniqueidentifier" character varying(64), --- link to partsmaster record
   
   "referencename" character varying(64),
   "universalresourceidentifier" character varying(64) not null,
   "fileidentifier" character varying(64),
   "versionidentifer" character varying(64),
   "filesize" int,
   "checksum" character varying(64),
   "isfilein" boolean, --- (yes | no )
   "description" character varying(512),
   "globalmimetypequalifiercode" character varying(64),
   "attachmentmodificationdate" timestamp with time zone,
   
   constraint "attachment_check" foreign key ("itemuniqueidentifier") 
   references "partsmaster" ("itemuniqueidentifier") 
   on delete cascade on update cascade,
   
   primary key ("itemuniqueidentifier", "universalresourceidentifier")
   );
   
