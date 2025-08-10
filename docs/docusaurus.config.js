import {themes as prismThemes} from 'prism-react-renderer';


/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Atlas',
  tagline: 'Atlas is a data-centric AI framework for curating, indexing massive dataset and training models.',
  favicon: 'update_image_path',

  // Future flags, see https://docusaurus.io/docs/api/docusaurus-config#future
  future: {
    v4: true, // Improve compatibility with the upcoming Docusaurus v4
  },

  // Set the production url of your site here
  url: 'http://localhost3000.com',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub pages deployment, it is often '/<projectName>/'
  baseUrl: '/',

  // GitHub pages deployment config.
  // If you aren't using GitHub pages, you don't need these.
  organizationName: 'facebook', // Usually your GitHub org/user name.
  projectName: 'docusaurus', // Usually your repo name.

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',
  url: 'https://senhorinfinito.github.io',
  baseUrl: '/atlas-ai/',
  projectName: 'atlas-ai',
  organizationName: 'senhorinfinito',
  deploymentBranch: 'gh-pages',


  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: [
      'en'
    ],  
  },

  presets: [
    [
      'classic',
      ({
        docs: {
          path : "docs",
          routeBasePath: "docs",
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl:
            'https://github.com/AyushExel/atlas-ai/tree/main/packages/create-docusaurus/templates/shared/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),

        },
      }),
    ],
  ],

  themeConfig:
  
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/.jpg',
      navbar: {
        title: 'Atlas',
        logo: {
          alt: 'logo will update',
          src: 'img/as.svg',
        },
        items: [
          {
            type : 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'right',
            label: 'Docs',
          },
          {
            href: 'https://github.com/AyushExel/atlas-ai',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'light',
        links: [],
        copyright: `Copyright © ${new Date().getFullYear()} Atlas.`,
      },
      prism: {
        theme: prismThemes.vsDark,
        darkTheme: prismThemes.vsLight,
      },
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: true,
      },
    }),
};




export default config;
