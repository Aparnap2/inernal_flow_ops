// prisma/seed.js
const { PrismaClient } = require('@prisma/client')

const prisma = new PrismaClient()

async function main() {
  // Create sample users
  const adminUser = await prisma.user.upsert({
    where: { email: 'admin@example.com' },
    update: {},
    create: {
      email: 'admin@example.com',
      name: 'Admin User',
      role: 'ADMIN',
    },
  })

  const operatorUser = await prisma.user.upsert({
    where: { email: 'operator@example.com' },
    update: {},
    create: {
      email: 'operator@example.com',
      name: 'Operator User',
      role: 'OPERATOR',
    },
  })

  const viewerUser = await prisma.user.upsert({
    where: { email: 'viewer@example.com' },
    update: {},
    create: {
      email: 'viewer@example.com',
      name: 'Viewer User',
      role: 'VIEWER',
    },
  })

  console.log('Seeded users:', { adminUser, operatorUser, viewerUser })

  // Create sample accounts
  const sampleAccounts = [
    {
      hubspotId: 'company_1',
      name: 'Acme Corporation',
      domain: 'acme.com',
      industry: 'Technology',
      employeeCount: 150,
      annualRevenue: 50000000,
      lifecycleStage: 'customer',
      lastModifiedDate: new Date(),
    },
    {
      hubspotId: 'company_2',
      name: 'Globex Inc',
      domain: 'globex.com',
      industry: 'Manufacturing',
      employeeCount: 3000,
      annualRevenue: 250000000,
      lifecycleStage: 'lead',
      lastModifiedDate: new Date(),
    },
    {
      hubspotId: 'company_3',
      name: 'Initech LLC',
      domain: 'initech.com',
      industry: 'Software',
      employeeCount: 50,
      annualRevenue: 10000000,
      lifecycleStage: 'marketingqualifiedlead',
      lastModifiedDate: new Date(),
    },
  ]

  for (const accountData of sampleAccounts) {
    await prisma.account.upsert({
      where: { hubspotId: accountData.hubspotId },
      update: {},
      create: accountData,
    })
  }

  console.log('Seeded sample accounts')

  // Create sample contacts
  const sampleContacts = [
    {
      hubspotId: 'contact_1',
      email: 'john.doe@acme.com',
      firstName: 'John',
      lastName: 'Doe',
      jobTitle: 'CTO',
      lifecycleStage: 'customer',
      lastModifiedDate: new Date(),
      accountId: (await prisma.account.findFirst({ where: { hubspotId: 'company_1' } }))?.id,
    },
    {
      hubspotId: 'contact_2',
      email: 'jane.smith@globex.com',
      firstName: 'Jane',
      lastName: 'Smith',
      jobTitle: 'VP Engineering',
      lifecycleStage: 'lead',
      lastModifiedDate: new Date(),
      accountId: (await prisma.account.findFirst({ where: { hubspotId: 'company_2' } }))?.id,
    },
  ]

  for (const contactData of sampleContacts) {
    await prisma.contact.upsert({
      where: { hubspotId: contactData.hubspotId },
      update: {},
      create: contactData,
    })
  }

  console.log('Seeded sample contacts')

  // Create sample deals
  const sampleDeals = [
    {
      hubspotId: 'deal_1',
      name: 'Enterprise License Agreement',
      stage: 'closedwon',
      amount: 100000,
      closeDate: new Date('2024-12-31'),
      probability: 0.95,
      lastModifiedDate: new Date(),
      accountId: (await prisma.account.findFirst({ where: { hubspotId: 'company_1' } }))?.id,
      contactId: (await prisma.contact.findFirst({ where: { hubspotId: 'contact_1' } }))?.id,
    },
    {
      hubspotId: 'deal_2',
      name: 'Professional Services Contract',
      stage: 'presentationscheduled',
      amount: 25000,
      closeDate: new Date('2025-03-31'),
      probability: 0.7,
      lastModifiedDate: new Date(),
      accountId: (await prisma.account.findFirst({ where: { hubspotId: 'company_2' } }))?.id,
      contactId: (await prisma.contact.findFirst({ where: { hubspotId: 'contact_2' } }))?.id,
    },
  ]

  for (const dealData of sampleDeals) {
    await prisma.deal.upsert({
      where: { hubspotId: dealData.hubspotId },
      update: {},
      create: dealData,
    })
  }

  console.log('Seeded sample deals')

  // Create sample policies
  const samplePolicies = [
    {
      name: 'High Value Deal Approval',
      description: 'Approvals required for deals over $50,000',
      version: '1.0',
      isActive: true,
      conditions: {
        "amount": { "gte": 50000 }
      },
      actions: {
        "requireApproval": true,
        "approvalType": "PROCUREMENT",
        "riskLevel": "MEDIUM"
      },
    },
    {
      name: 'Enterprise Account Processing',
      description: 'Special handling for enterprise accounts with >1000 employees',
      version: '1.0',
      isActive: true,
      conditions: {
        "employeeCount": { "gt": 1000 },
        "industry": { "in": ["Government", "Healthcare", "Financial Services"] }
      },
      actions: {
        "requireApproval": true,
        "approvalType": "RISK_THRESHOLD",
        "riskLevel": "HIGH"
      },
    },
  ]

  for (const policyData of samplePolicies) {
    await prisma.policy.upsert({
      where: { name: policyData.name },
      update: {},
      create: policyData,
    })
  }

  console.log('Seeded sample policies')

  console.log('Database seeding completed!')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })