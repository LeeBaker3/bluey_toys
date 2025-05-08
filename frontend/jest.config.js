const nextJest = require('next/jest')

const createJestConfig = nextJest({
  // Provide the path to your Next.js app to load next.config.js and .env files in your test environment
  dir: './',
})

// Add any custom config to be passed to Jest
const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],
  testEnvironment: 'jest-environment-jsdom',
  transform: {
    // Directly point to the SWC transformer provided by Next.js, without the empty options object
    '^.+\\.(js|jsx|ts|tsx)$': 'next/dist/build/swc/jest-transformer.js',
  },
}

module.exports = createJestConfig(customJestConfig)