import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

async function main() {
  await prisma.media.createMany({
    data: [
      { id: 'dfl' },
      { id: 'mad lads' },
      { id: 'bonk' },
      { id: 'okay' },
      { id: 'parcl' },
      { id: 'tensorians' },
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
