import { Prisma, PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();
import { faker } from '@faker-js/faker';

async function main() {
  await prisma.media.createMany({
    data: [
      { id: 'jupiter' },
      { id: 'kamino' },
      { id: 'tensor' },
      { id: 'metaplex' },
    ],
  });

  await prisma.leaderboard.createMany({
    data: Array.from({ length: 200 }).map(
      (): Prisma.LeaderboardCreateManyInput => {
        const res = {
          walletId: fakeSolanaAddress(),
          pluginsUsed: Math.floor(Math.random() * 100),
          myPluginsUsed: Math.floor(Math.random() * 100),
          transactionsMade: Math.floor(Math.random() * 100),
        };
        return {
          ...res,
          score: res.pluginsUsed + res.myPluginsUsed + res.transactionsMade,
        };
      },
    ),
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

function fakeSolanaAddress(): string {
  return faker.string.alphanumeric({
    length: 43,
    exclude: ['O', 'I', 'l'],
  });
}
