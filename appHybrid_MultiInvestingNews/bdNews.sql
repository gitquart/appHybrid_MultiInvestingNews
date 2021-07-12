

CREATE TABLE tbControl (
        ID INT primary key,
        app varchar(50),
        limit_iteration int,
        lsControl varchar(50),
        noinfolimit int,
        page int,
        query varchar(50)
);


insert into tbcontrol  values (1,'Trading news search',0,'',0,1,'No query');

create table tbCommonTools
(
        ID INT primary key,
        lsOwnStopWords text



)

drop table tbnew ;
select app,page from tbcontrol where id=1;

update tbcontrol  set page=1 where id=1;

/'News content'/
CREATE TABLE tbNew (
        ID SERIAL primary key,
        txtTitle text,
        txtNew_content_Original text,
        txtNew_content_Translated text,
        txtBase64_contentOriginal text,
        tspDateTime timestamp,
        txturl varchar(200),
        txtsitesource varchar(100),
        commodity varchar(50),
        lsKeywordsOriginal text,
        lsKeyWordsTranslated text,
        appName varchar(20)
);

select * from tbNew;

delete from tbnew where id=24;

