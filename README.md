Catalog Permissions
Catalog permissions define which principals can read and/or write to a particular catalog version. If a product content management process (PIM/PCM) with different parties is in place, such permissions should be used to avoid accidental or unauthorized modification of product content. Catalog permissions are assigned on catalog version level, that is for a principal, different permissions can be assigned for the Staged and Online Version of a catalog.

For the PMI-DCE2.0 SAP Commerce system such permissions are obviously in use.

The following table shows all read- and write principals (user groups and individuals), which have read and/or write permission on catalog versions (product catalogs only). While such permissions exist they are not well maintained:
**table**
Above permission configuration is likely to become unmaintainable soon. By viewing the backoffice user management perspective, is not possible to tell which permissions a user has on a particular catalog version. Maintainability is negatively affected.

The following practices should be followed when modelling catalog permissions:

Individual users should not directly be assigned to the list of catalog read- or write principals. Instead they should inherit such permission from a user group through membership.
User groups should not directly be assigned to the list of catalog read- or write principals. Instead they should inherit the permission from a dedicated user group created for the particular permission on a particular catalog version.
SEC-07

Re-organize the catalog read/write permissions in order to keep them maintainable.

Avoid granting catalog permissions directly to users. Introduce dedicated "reader" and "writer" groups per catalog version to serve as an indirection for catalog access management.

SAP Security - Development Task: 


USE CASE 2:

Total refactors of the current structure, which consists of:

 1) creating two groups ($release_productCatalog_reader, $release_productCatalog_reader) which contain all groups with read and write permissions respectively.

UPDATE CatalogVersion; catalog(id)[unique = true]  ; version[unique = true]; readPrincipals(uid)[mode = append]; writePrincipals(uid)[mode = append]
                     ; pmi-$release-ProductCatalog ; Online                ; $release_productCatalog_reader    ;
                     ; pmi-$release-ProductCatalog ; Staged                ; $release_productCatalog_reader    ;$release_productCatalog_writer

2) $release_productCatalog_write will be member of $release_productCatalog_reader;

3) a group with write permission will put on the writer, and a group with read permission will put on the reader.

4) List of groups for which reorganisation is necessary (approx. 400):

globalConfiguratorRole 
marketCatalogApproverRole_xx 
marketCatalogEditorRole_xx 
marketCatalogPriceEditorRole_xx
marketCatalogPublisherRole_xx 
marketDeploymentManagerRole 
marketDeploymentManagerRole_$release
pimFireFighterRole 
productApproverRole
productApproverRole_$release
productEditorRole
productEditorRole_$release
productPriceEditorRole
productPriceEditorRole_$release
productPublishRole
productPublishRole_$release
marketDeploymentManagerCountryVisibility
marketDeploymentManagerCountryVisibility_$release
wfl_productApproverGroup
wfl_productApproverGroup_$release
wfl_productEditorGroup
wfl_productEditorGroup_$release
wfl_productPriceEditorGroup
wfl_productPriceEditorGroup_$release
wfl_productPublishGroup
wfl_productPublishGroup_$release
marketingManagerGroup,
restrictedMarketingManagerGroup,
globalViewerRole,
auditLogViewerRole,
consumerViewerRole,
orderViewerRole,
promotionPublisherRole,
promotionEditorRole,
ordersFireFighterRole,
promotionCountryVisibility,
orderViewerVisibility,
consumerViewerRole_$release,
orderViewerRole_$release,
fraudManagerRole_$release,
marketCatalogApproverRole_xx,
stockViewerRole,
supervisorRole_$release

 

Example to HOW TO FIX for DE
UPDATE CatalogVersion; catalog(id)[unique = true]  ; version[unique = true]; readPrincipals(uid)[mode = append]; writePrincipals(uid)[mode = append]
                     ; pmi-de-ProductCatalog ; Online                ; de_productCatalog_reader    ;
                     ; pmi-de-ProductCatalog ; Staged                ; de_productCatalog_reader    ;de_productCatalog_writer

INSERT_UPDATE PrincipalGroupRelation; source(uid)[unique = true]      ; target(uid)[unique = true]
                                    ; de_productCatalog_writer      ;de_productCatalog_reader
                                    ; de_productCatalog_writer      ;(wfl_productPublishGroup,wfl_productPriceEditorGroup_de,wfl_productEditorGroup_de,wfl_productApproverGroup_de,globalConfiguratorRole,marketDeploymentManagerRole,globalItSupportManagerRole,pimFireFighterRole,marketDeploymentManagerCountryVisibility_de,marketDeploymentManagerRole_de,productApproverRole_de,productEditorRole_de,productPriceEditorRole_de,marketCatalogPriceEditorRole_xx,marketCatalogEditorRole_xx,marketCatalogPublisherRole_xx)
                                    ; de_productCatalog_reader        ;(marketingManagerGroup,restrictedMarketingManagerGroup,globalViewerRole,auditLogViewerRole,consumerViewerRole,orderViewerRole,promotionPublisherRole,promotionEditorRole,ordersFireFighterRole,promotionCountryVisibility,orderViewerVisibility,consumerViewerRole_de,orderViewerRole_de,fraudManagerRole_de,marketCatalogApproverRole_xx,stockViewerRole,supervisorRole_de)

A thorough estimation per country is necessary to check whether all associated roles are actually needed or not.
At the moment in PROD we have 24 countries, 2 SP of estimation for each country.
Story points : 35 SP on dev side;

 

Further days of testing will then be added to the estimate, to assess that everything continues to function properly.

--------------------

Analysis task: https://jira.pmidce.com/browse/DCE20HOME-226330



