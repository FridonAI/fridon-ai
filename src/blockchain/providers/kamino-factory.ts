import { ComputeBudgetProgram, Connection, PublicKey } from '@solana/web3.js';
import {
  KaminoAction,
  KaminoMarket,
  KaminoObligation,
  KaminoReserve,
  PROGRAM_ID,
  Position,
  VanillaObligation,
  buildVersionedTransaction,
} from '@hubbleprotocol/kamino-lending-sdk';
import { TokenAmount } from '../utils/tools/token-amount';
import {
  DONATION_ADDRESS,
  KAMINO_MAIN_MARKET_ADDRESS,
  PRIORITY_FEE,
} from '../utils/constants';
import { HttpException, Injectable } from '@nestjs/common';
import { NumberFormatter } from '../utils/tools/number-formatter';

export interface MarketInfo {
  name: string;
  address: PublicKey;
  lutAddress: PublicKey;
}

export const MARKETS: MarketInfo[] = [
  {
    name: 'Main Market',
    address: new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'),
    lutAddress: new PublicKey('284iwGtA9X9aLy3KsyV8uT2pXLARhYbiSi5SiM2g47M2'),
  },
  {
    name: 'JLP Market',
    address: new PublicKey('DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek'),
    lutAddress: new PublicKey('GprZNyWk67655JhX6Rq9KoebQ6WkQYRhATWzkx2P2LNc'),
  },
  {
    name: 'Altcoins Market',
    address: new PublicKey('ByYiZxp8QrdN9qbdtaAiePN8AAr3qvTPppNJDpf5DVJ5'),
    lutAddress: new PublicKey('x2uEQSaqrZs5UnyXjiNktRhrAy6iNFeSKai9VNYFFuy'),
  },
];

@Injectable()
export class KaminoFactory {
  constructor(private connection: Connection) {}
  private getReserve(
    market: KaminoMarket,
    mintAddr: string,
  ): KaminoReserve | undefined {
    const { reserves } = market;
    let result: KaminoReserve | undefined = undefined;

    reserves.forEach((reserve) => {
      const {
        stats: { mintAddress },
      } = reserve;
      if (mintAddress.toBase58() === mintAddr) {
        result = reserve;
      }
    });

    return result;
  }

  private async getMintAddresses(market: KaminoMarket) {
    const { reserves } = market;

    const mintAddresses: string[] = [];
    reserves.forEach((reserve) => {
      const {
        stats: { mintAddress },
      } = reserve;
      mintAddresses.push(mintAddress.toBase58());
    });

    return mintAddresses;
  }

  private getMarketAddress(mintAddress: string): MarketInfo | undefined {
    // Check for wif, bonk,wen, pyth and return altcoins market lut address
    if (
      mintAddress === 'EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm' || // wif
      mintAddress === 'DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263' || // bonk
      mintAddress === '3J5QaP1zJN9yXE7jr5XJa3Lq2TyGHSHu2wssK7N1Aw4p' || // wen
      mintAddress === 'HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3' // pyth
    ) {
      return MARKETS[2];
    }

    // If not return MainMarket
    return MARKETS[0];
  }

  private async getMarket(mintAddress: string) {
    const marketInfo = this.getMarketAddress(mintAddress);

    if (!marketInfo) {
      throw new HttpException('Market not found', 404);
    }

    const market = await KaminoMarket.load(this.connection, marketInfo.address);

    if (market == null) {
      throw new HttpException("Couldn't load market", 403);
    }

    return {
      market,
      marketInfo,
    };
  }

  async supply(walletAddress: string, mintAddress: string, amount: number) {
    const payer = new PublicKey(walletAddress);

    const { market, marketInfo } = await this.getMarket(mintAddress);

    const reserve = this.getReserve(market, mintAddress);

    if (!reserve) {
      throw new HttpException(
        `Couldn't find reserve on Kamino to deposit.`,
        404,
      );
    }

    const tokenAmount = new TokenAmount(
      amount,
      reserve.stats.decimals,
      false,
    ).toWei();

    const kaminoAction = await KaminoAction.buildDepositTxns(
      market,
      tokenAmount.toString(),
      new PublicKey(mintAddress),
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
      0,
      undefined,
      undefined,
      undefined,
      DONATION_ADDRESS,
    );

    const priorityPrice = ComputeBudgetProgram.setComputeUnitPrice({
      microLamports: PRIORITY_FEE,
    });

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
      priorityPrice,
    ];

    const transaction = await buildVersionedTransaction(
      this.connection,
      payer,
      instructions,
      [marketInfo.lutAddress],
    );

    return transaction;
  }

  async borrow(
    walletAddress: string,
    mintAddress: string,
    amount: number,
    connection: Connection,
  ) {
    const payer = new PublicKey(walletAddress);
    const { market } = await this.getMarket(mintAddress);

    const reserve = this.getReserve(market, mintAddress);
    if (!reserve) {
      throw new HttpException(
        "Couldn't find reserve on Kamino to Borrow.",
        404,
      );
    }

    const tokenAmount = new TokenAmount(
      amount,
      reserve.stats.decimals,
      false,
    ).toWei();
    const kaminoAction = await KaminoAction.buildBorrowTxns(
      market,
      tokenAmount.toString(),
      new PublicKey(mintAddress),
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
      0,
      true,
      false,
      true,
      DONATION_ADDRESS,
    );

    const priorityPrice = ComputeBudgetProgram.setComputeUnitPrice({
      microLamports: PRIORITY_FEE,
    });
    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
      priorityPrice,
    ];

    const transaction = await buildVersionedTransaction(
      connection,
      payer,
      instructions,
    );

    return transaction;
  }

  async repay(
    walletAddress: string,
    mintAddress: string,
    amount: number,
    connection: Connection,
  ) {
    const payer = new PublicKey(walletAddress);
    const { market } = await this.getMarket(mintAddress);

    const reserve = this.getReserve(market, mintAddress);
    if (!reserve) {
      throw new HttpException("Couldn't find reserve on Kamino to Repay", 404);
    }

    const tokenAmount = new TokenAmount(
      amount,
      reserve.stats.decimals,
      false,
    ).toWei();
    const slot = await this.connection.getSlot();
    const kaminoAction = await KaminoAction.buildRepayTxns(
      market,
      tokenAmount.toString(),
      new PublicKey(mintAddress),
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
      slot,
      undefined,
      0,
      true,
      undefined,
      undefined,
      DONATION_ADDRESS,
    );

    const priorityPrice = ComputeBudgetProgram.setComputeUnitPrice({
      microLamports: PRIORITY_FEE,
    });

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
      priorityPrice,
    ];

    const transaction = await buildVersionedTransaction(
      connection,
      payer,
      instructions,
    );

    return transaction;
  }

  async withdraw(
    walletAddress: string,
    mintAddress: string,
    amount: number,
    connection: Connection,
  ) {
    const payer = new PublicKey(walletAddress);
    const { market } = await this.getMarket(mintAddress);

    const reserve = this.getReserve(market, mintAddress);

    if (!reserve) {
      throw new HttpException(
        "Couldn't find reserve on Kamino to Withdraw.",
        404,
      );
    }

    const tokenAmount = new TokenAmount(
      amount,
      reserve.stats.decimals,
      false,
    ).toWei();
    const kaminoAction = await KaminoAction.buildWithdrawTxns(
      market,
      tokenAmount.toString(),
      new PublicKey(mintAddress),
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
      0,
      true,
      undefined,
      undefined,
      DONATION_ADDRESS,
    );

    const priorityPrice = ComputeBudgetProgram.setComputeUnitPrice({
      microLamports: PRIORITY_FEE,
    });

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
      priorityPrice,
    ];

    const transaction = await buildVersionedTransaction(
      connection,
      payer,
      instructions,
    );

    return transaction;
  }

  async getKaminoBalances(
    walletAddress: string,
    mintAddress: string | undefined,
    currency?: string | undefined,
  ) {
    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new HttpException("Couldn't load market", 403);
    }

    const mintAddresses = await this.getMintAddresses(market);
    if (mintAddress) {
      if (!mintAddresses.includes(mintAddress)) {
        throw new HttpException('Mint address not supported on Kamino', 404);
      }
    }

    const obligations = await market.getObligationByWallet(
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
    );

    if (!obligations) {
      const message = mintAddress
        ? `Your balance for ${currency} is 0`
        : 'Your Kamino balance is 0';
      throw new HttpException(message, 403); // User is new
    }

    const deposits = this.getDeposits(obligations);
    const borrows = this.getBorrows(obligations);

    if (mintAddress) {
      const filteredDeposits = deposits.filter((x) =>
        x.mintAddress.equals(new PublicKey(mintAddress)),
      );
      const filteredBorrows = borrows.filter((x) =>
        x.mintAddress.equals(new PublicKey(mintAddress)),
      );

      if (filteredDeposits.length == 0 && filteredBorrows.length == 0) {
        throw new HttpException(`Your balance for ${currency} is 0`, 403);
      }

      return {
        deposits: filteredDeposits,
        borrows: filteredBorrows,
      };
    }

    return {
      deposits,
      borrows,
    };
  }

  async getKaminoDepositions(
    walletAddress: string,
    mintAddress: string | undefined,
    currency?: string | undefined,
  ) {
    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new HttpException("Couldn't load market", 403);
    }

    const mintAddresses = await this.getMintAddresses(market);
    if (mintAddress) {
      if (!mintAddresses.includes(mintAddress)) {
        throw new HttpException(`${currency} not supported on Kamino.`, 404);
      }
    }

    const obligations = await market.getObligationByWallet(
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
    );

    if (!obligations) {
      const message = currency
        ? `Your deposit balance for ${currency} is 0`
        : 'Your Kamino balance is 0';
      throw new HttpException(message, 403); // User is new
    }

    if (mintAddress) {
      const deposit = this.getDeposit(obligations, new PublicKey(mintAddress));

      if (!deposit) {
        throw new HttpException(
          `Your deposit balance for ${currency} is 0`,
          403,
        );
      }

      return [deposit];
    } else {
      return this.getDeposits(obligations);
    }
  }

  async getKaminoBorrows(
    walletAddress: string,
    mintAddress: string | undefined,
    currency?: string | undefined,
  ) {
    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new HttpException("Couldn't load market", 403);
    }

    const mintAddresses = await this.getMintAddresses(market);
    if (mintAddress) {
      if (!mintAddresses.includes(mintAddress)) {
        throw new HttpException('Mint address not supported on Kamino', 404);
      }
    }

    const obligations = await market.getObligationByWallet(
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
    );

    if (!obligations) {
      const message = currency
        ? `Your deposit balance for ${currency} is 0`
        : 'Your Kamino balance is 0';

      throw new HttpException(message, 403); // User is new
    }

    if (mintAddress) {
      const borrowed = this.getBorrow(obligations, new PublicKey(mintAddress));

      if (!borrowed) {
        const message = currency
          ? `Your borrow balance for ${currency} is 0`
          : 'Your Kamino balance is 0';
        throw new HttpException(message, 403);
      }

      return [borrowed];
    } else {
      return this.getBorrows(obligations);
    }
  }

  private getDeposits(_nativeObligation: KaminoObligation): Position[] {
    return Array.from(_nativeObligation.deposits.values());
  }

  private getBorrows(_nativeObligation: KaminoObligation): Position[] {
    return Array.from(_nativeObligation.borrows.values());
  }

  private getBorrow(
    _nativeObligation: KaminoObligation,
    mintAddress: PublicKey,
  ): Position | undefined {
    return this.getBorrows(_nativeObligation).find((x) =>
      x.mintAddress.equals(mintAddress),
    );
  }

  private getDeposit(
    _nativeObligation: KaminoObligation,
    mintAddress: PublicKey,
  ): Position | undefined {
    return this.getDeposits(_nativeObligation).find((x) =>
      x.mintAddress.equals(mintAddress),
    );
  }
}

@Injectable()
export class KaminoBalances {
  constructor(
    readonly _nativeObligation: KaminoObligation,
    readonly utils: NumberFormatter,
  ) {}

  get nativeObligation() {
    return this._nativeObligation;
  }

  get deposits(): Position[] {
    return Array.from(this.nativeObligation.deposits.values());
  }

  get borrows(): Position[] {
    return Array.from(this.nativeObligation.borrows.values());
  }

  getBorrow(mintAddress: PublicKey): Position | undefined {
    return Array.from(this.nativeObligation.borrows.values()).find((x) =>
      x.mintAddress.equals(mintAddress),
    );
  }

  getDeposit(mintAddress: PublicKey): Position | undefined {
    return Array.from(this.nativeObligation.deposits.values() ?? []).find((x) =>
      x.mintAddress.equals(mintAddress),
    );
  }

  get totalBorrowed() {
    return this.nativeObligation.refreshedStats.userTotalBorrow;
  }

  get totalBorrowedFormatted() {
    return this.utils.toFormattedUsd(this.totalBorrowed);
  }

  get totalSupplied() {
    return this.nativeObligation.refreshedStats.userTotalDeposit;
  }

  get totalSuppliedFormatted() {
    return this.utils.toFormattedUsd(this.totalSupplied);
  }

  get borrowPower() {
    const { borrowLimit, userTotalBorrowBorrowFactorAdjusted } =
      this.nativeObligation.refreshedStats;
    return borrowLimit.minus(userTotalBorrowBorrowFactorAdjusted);
  }

  get borrowPowerFormatted() {
    return this.utils.toFormattedUsd(this.borrowPower);
  }

  get ltv() {
    return this.nativeObligation.refreshedStats.loanToValue;
  }

  get ltvFormatted() {
    return this.utils.toFormattedPercent(this.ltv);
  }

  get maxLtv() {
    const { borrowLimit, userTotalDeposit } =
      this.nativeObligation.refreshedStats;
    return borrowLimit.div(userTotalDeposit);
  }

  get maxLtvFormatted() {
    return this.utils.toFormattedPercent(this.maxLtv);
  }

  get liquidationLtv() {
    return this.nativeObligation.refreshedStats.liquidationLtv;
  }

  get liquidationLtvFormatted() {
    return this.utils.toFormattedPercent(this.liquidationLtv);
  }
}
