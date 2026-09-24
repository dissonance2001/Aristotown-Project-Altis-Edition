import { defineConfig } from '@prisma/internals'

export default defineConfig({
  schema: './schema.prisma',
  datasource: {
    url: process.env.DATABASE_URL,
  },
})