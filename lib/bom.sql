create table if not exists bom (
   "itemuniqueidentifier" character varying(64), --- link to partsmaster record; source
   
   "revisionidentifier" character varying(64),
   "isserializationrequired" boolean, --- (yes | no )
   "globalbillofmaterialtypecode" character varying(24), --- (directmaterial | indirectmaterial | subassembly | phantomsubassembly | endproduct | kit | setup | asneeded | reference | nontangible | other )
   "globalbillofmaterialtypecodeother" character varying(64),
   "notes" character varying(1024),
   "billofmaterialitemidentifier" character varying(64),
   "billofmaterialitemuniqueidentifier" character varying(64), --- target
   "itemquantity" float, --- could be fractional number!
   "globalproductquantitytypecode" character varying(24), --- (perassembly | persetup | asneeded | shrinkage | other )
   "globalproductquantitytypecodeother" character varying(64),
   "description" character varying(512),
   "proprietarysequenceidentifier" character varying(64),
   
   constraint "bom_src_check" foreign key ("itemuniqueidentifier") 
   references "partsmaster" ("itemuniqueidentifier")
   on delete cascade on update cascade,

   constraint "bom_tgt_check" foreign key ("billofmaterialitemuniqueidentifier")
   references "partsmaster" ("itemuniqueidentifier")
   on delete cascade on update cascade,
   
   primary key ("itemuniqueidentifier", "billofmaterialitemuniqueidentifier")
   );
   
