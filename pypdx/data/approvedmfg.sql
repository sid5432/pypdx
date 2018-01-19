create table if not exists approvedmfg (
   "itemuniqueidentifier" character varying(64), --- link to partsmaster record
   
   "manufacturerpartidentifier" character varying(64) not null,
   "manufacturerpartuniqueidentifier" character varying(64),
   "manufacturercontactuniqueidentifier" character varying(64),
   "globalmanufacturerpartstatuscode" character varying(64), --- approved | qualityhold | underqualification | unqualified | disqualified | obsolete | nonpreferred | conditional | reference | other
   "globalmanufacturerpartstatuscodeother" character varying(64),
   "globalpreferredstatuscode" character varying(64),
   "description" character varying(512),
   "manufacturedby" character varying(128),
   
   constraint "approvedmfg_check" foreign key ("itemuniqueidentifier") 
   references "partsmaster" ("itemuniqueidentifier") 
   on delete cascade on update cascade,
   
   primary key ("itemuniqueidentifier", "manufacturedby", "manufacturerpartidentifier")
   );
   
