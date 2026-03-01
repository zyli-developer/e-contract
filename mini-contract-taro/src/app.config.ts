export default defineAppConfig({
  pages: [
    'pages/index/index',
    'pages/login/index',
    'pages/register/index',
    'pages/contract-manage/index',
    'pages/contract-detail/index',
    'pages/contract-sign/index',
    'pages/contract-create/index',
    'pages/template-market/index',
    'pages/template-detail/index',
    'pages/profile/index',
    'pages/profile/seals/index',
    'pages/profile/seal-create/index',
    'pages/profile/settings/index',
    'pages/profile/realname/index',
  ],
  tabBar: {
    color: '#999999',
    selectedColor: '#00C28A',
    backgroundColor: '#ffffff',
    list: [
      {
        pagePath: 'pages/index/index',
        text: '首页',
        iconPath: 'assets/tabbar/home.png',
        selectedIconPath: 'assets/tabbar/home-active.png',
      },
      {
        pagePath: 'pages/contract-manage/index',
        text: '合同',
        iconPath: 'assets/tabbar/contract.png',
        selectedIconPath: 'assets/tabbar/contract-active.png',
      },
      {
        pagePath: 'pages/profile/index',
        text: '我的',
        iconPath: 'assets/tabbar/profile.png',
        selectedIconPath: 'assets/tabbar/profile-active.png',
      },
    ],
  },
  window: {
    backgroundTextStyle: 'light',
    navigationBarBackgroundColor: '#00C28A',
    navigationBarTitleText: 'Mini Contract',
    navigationBarTextStyle: 'white',
  },
})
