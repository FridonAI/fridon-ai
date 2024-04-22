import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  await prisma.media.createMany({
    data: [
      { id: 'jupiter' },
      { id: 'kamino' },
      { id: 'tensor' },
      { id: 'metaplex' },
    ],
  });
}

main()
  .then(async () => {
    await prisma.$disconnect();
  })
  .catch(async (e) => {
    console.error(e);
    await prisma.$disconnect();
    process.exit(1);
  });
