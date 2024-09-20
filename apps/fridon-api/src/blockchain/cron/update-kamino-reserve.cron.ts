import { Inject, Logger } from '@nestjs/common';
import { Cron, CronExpression } from '@nestjs/schedule';
import { CACHE_MANAGER } from '@nestjs/cache-manager';
import { Cache } from 'cache-manager';
import { Connection } from '@solana/web3.js';
import { KaminoMarket } from '@hubbleprotocol/kamino-lending-sdk';
import { KAMINO_MAIN_MARKET_ADDRESS } from '../utils/constants';

export class UpdateKaminoReserve {
  private readonly l = new Logger(UpdateKaminoReserve.name);

  constructor(
    @Inject(CACHE_MANAGER) private cacheManager: Cache,
    readonly connection: Connection,
  ) {}

  @Cron(CronExpression.EVERY_DAY_AT_MIDNIGHT)
  async execute() {
    this.l.log('Called Update Token List Cron Job');
    this.cacheManager;

    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (!market) {
      this.l.error("Couldn't load market");
      return;
    }

    const { reserves } = market;

    const vaultInformation: KaminoVaultType[] = [];
    reserves.forEach((reserve) => {
      const {
        symbol,
        address,
        stats: {
          // Token decimals
          decimals,
          // Token address
          mintAddress,
          loanToValuePct,
          // Max token amount to deposit
          reserveDepositLimit,
          // Max token amount to borrow
          reserveBorrowLimit,
          // Collateral yield bearing token supply
          mintTotalSupply,
        },
      } = reserve;
      const totalSupply = reserve.getTotalSupply();
      const totalBorrows = reserve.getBorrowedAmount();
      const depositTvl = reserve.getDepositTvl();

      const data: KaminoVaultType = {
        symbol,
        address: address.toBase58(),
        decimals,
        mintAddress: mintAddress.toBase58(),
        loanToValuePct,
        reserveDepositLimit: reserveDepositLimit
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        reserveBorrowLimit: reserveBorrowLimit
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        mintTotalSupply: mintTotalSupply.toString(),
        totalSupply: totalSupply
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        totalBorrows: totalBorrows
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        depositTvl: depositTvl.toString(),
      };

      vaultInformation.push(data);
    });

    await this.cacheManager.set(
      'kamino-vaults',
      vaultInformation,
      24 * 60 * 60 * 1000,
    );
  }
}

export type KaminoVaultType = {
  symbol: string;
  address: string;
  decimals: number;
  mintAddress: string;
  loanToValuePct: number;
  reserveDepositLimit: string;
  reserveBorrowLimit: string;
  mintTotalSupply: string;
  totalSupply: string;
  totalBorrows: string;
  depositTvl: string;
};
