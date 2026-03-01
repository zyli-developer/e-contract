module.exports = {
  testEnvironment: 'jsdom',
  transform: {
    '^.+\\.(ts|tsx|js|jsx)$': ['babel-jest', {
      presets: [
        ['@babel/preset-react', { runtime: 'automatic' }],
        '@babel/preset-typescript',
      ],
    }],
  },
  moduleNameMapper: {
    '^@/(.*)$': '<rootDir>/src/$1',
    '^@tarojs/taro$': '<rootDir>/src/__tests__/__mocks__/taro.ts',
    '^@tarojs/components$': '<rootDir>/src/__tests__/__mocks__/components.tsx',
    '\\.(css|scss|sass)$': '<rootDir>/src/__tests__/__mocks__/style.ts',
  },
  setupFilesAfterEnv: ['@testing-library/jest-dom'],
  testMatch: ['<rootDir>/src/__tests__/**/*.test.(ts|tsx)'],
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json'],
}
