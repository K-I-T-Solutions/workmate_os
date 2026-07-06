import React from 'react';
import ComponentCreator from '@docusaurus/ComponentCreator';

export default [
  {
    path: '/workmate_os/',
    component: ComponentCreator('/workmate_os/', '170'),
    exact: true
  },
  {
    path: '/workmate_os/',
    component: ComponentCreator('/workmate_os/', 'abb'),
    routes: [
      {
        path: '/workmate_os/',
        component: ComponentCreator('/workmate_os/', '115'),
        routes: [
          {
            path: '/workmate_os/',
            component: ComponentCreator('/workmate_os/', '65d'),
            routes: [
              {
                path: '/workmate_os/backend',
                component: ComponentCreator('/workmate_os/backend', 'ee0'),
                exact: true,
                sidebar: "backendSidebar"
              },
              {
                path: '/workmate_os/backend/ADMIN_PANEL',
                component: ComponentCreator('/workmate_os/backend/ADMIN_PANEL', 'dd4'),
                exact: true,
                sidebar: "backendSidebar"
              },
              {
                path: '/workmate_os/backend/AUTHENTICATION',
                component: ComponentCreator('/workmate_os/backend/AUTHENTICATION', '01b'),
                exact: true,
                sidebar: "backendSidebar"
              },
              {
                path: '/workmate_os/backend/MODULE_UEBERSICHT',
                component: ComponentCreator('/workmate_os/backend/MODULE_UEBERSICHT', '9fb'),
                exact: true,
                sidebar: "backendSidebar"
              },
              {
                path: '/workmate_os/backoffice',
                component: ComponentCreator('/workmate_os/backoffice', 'bf8'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/backoffice/datenbank_schema',
                component: ComponentCreator('/workmate_os/backoffice/datenbank_schema', '24a'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/backoffice/modul_uebersicht',
                component: ComponentCreator('/workmate_os/backoffice/modul_uebersicht', '5c2'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/core',
                component: ComponentCreator('/workmate_os/core', '10a'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/core/api_endpoints',
                component: ComponentCreator('/workmate_os/core/api_endpoints', '2a7'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/core/core_erm',
                component: ComponentCreator('/workmate_os/core/core_erm', '190'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/core/entities',
                component: ComponentCreator('/workmate_os/core/entities', '209'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/core/flows',
                component: ComponentCreator('/workmate_os/core/flows', '359'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/core/workmate_os_core',
                component: ComponentCreator('/workmate_os/core/workmate_os_core', '67b'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance',
                component: ComponentCreator('/workmate_os/finance', '40f'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/de',
                component: ComponentCreator('/workmate_os/finance/de', '49c'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/de/analyse',
                component: ComponentCreator('/workmate_os/finance/de/analyse', 'c89'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/de/architektur',
                component: ComponentCreator('/workmate_os/finance/de/architektur', '9c8'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/de/schnellreferenz',
                component: ComponentCreator('/workmate_os/finance/de/schnellreferenz', '85f'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/en',
                component: ComponentCreator('/workmate_os/finance/en', '268'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/en/analysis',
                component: ComponentCreator('/workmate_os/finance/en/analysis', '101'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/en/architecture',
                component: ComponentCreator('/workmate_os/finance/en/architecture', 'd02'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/finance/en/quick_reference',
                component: ComponentCreator('/workmate_os/finance/en/quick_reference', '1a8'),
                exact: true,
                sidebar: "backofficeAndCoreSidebar"
              },
              {
                path: '/workmate_os/frontend',
                component: ComponentCreator('/workmate_os/frontend', '96d'),
                exact: true,
                sidebar: "frontendSidebar"
              },
              {
                path: '/workmate_os/frontend',
                component: ComponentCreator('/workmate_os/frontend', 'c53'),
                exact: true,
                sidebar: "frontendSidebar"
              },
              {
                path: '/workmate_os/frontend/architecture',
                component: ComponentCreator('/workmate_os/frontend/architecture', '7ac'),
                exact: true,
                sidebar: "frontendSidebar"
              },
              {
                path: '/workmate_os/frontend/quick_reference',
                component: ComponentCreator('/workmate_os/frontend/quick_reference', '7f0'),
                exact: true,
                sidebar: "frontendSidebar"
              },
              {
                path: '/workmate_os/frontend/visual_guide',
                component: ComponentCreator('/workmate_os/frontend/visual_guide', '06e'),
                exact: true,
                sidebar: "frontendSidebar"
              },
              {
                path: '/workmate_os/',
                component: ComponentCreator('/workmate_os/', '42a'),
                exact: true
              }
            ]
          }
        ]
      }
    ]
  },
  {
    path: '*',
    component: ComponentCreator('*'),
  },
];
