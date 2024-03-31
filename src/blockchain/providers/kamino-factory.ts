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
import { Injectable } from '@nestjs/common';
import { NumberFormatter } from '../utils/tools/number-formatter';

@Injectable()
export class KaminoFactory {
  constructor(private connection: Connection) {}

  async getKaminoPoints(walletAddress: string) {
    try {
      const request = await fetch(
        `https://api.hubbleprotocol.io/points/users/${walletAddress}/breakdown?env=mainnet-beta&source=Season1`,
      );
      const response = await request.json();

      const totalPointsEarnedNumber = parseFloat(response.totalPointsEarned);
      return Math.round(totalPointsEarnedNumber * 100) / 100;
    } catch (error) {
      console.error('Error while fetching user points', error);
      throw new Error('Error while fetching user points');
    }
  }

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

  async supply(
    walletAddress: string,
    mintAddress: string,
    amount: number,
    connection: Connection,
  ) {
    const payer = new PublicKey(walletAddress);
    const market = await KaminoMarket.load(
      connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const reserve = this.getReserve(market, mintAddress);

    if (!reserve) {
      throw new Error("Couldn't find reserve");
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
      connection,
      payer,
      instructions,
      [new PublicKey('284iwGtA9X9aLy3KsyV8uT2pXLARhYbiSi5SiM2g47M2')],
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
    const market = await KaminoMarket.load(
      connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const reserve = this.getReserve(market, mintAddress);
    if (!reserve) {
      throw new Error("Couldn't find reserve");
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
    const market = await KaminoMarket.load(
      connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const reserve = this.getReserve(market, mintAddress);
    if (!reserve) {
      throw new Error("Couldn't find reserve");
    }

    const tokenAmount = new TokenAmount(
      amount,
      reserve.stats.decimals,
      false,
    ).toWei();
    const kaminoAction = await KaminoAction.buildRepayTxns(
      market,
      tokenAmount.toString(),
      new PublicKey(mintAddress),
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
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
    const market = await KaminoMarket.load(
      connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const reserve = this.getReserve(market, mintAddress);

    if (!reserve) {
      throw new Error("Couldn't find reserve");
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

  async getKaminoBalances(walletAddress: string) {
    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const obligations = await market.getObligationByWallet(
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
    );

    if (!obligations) {
      throw new Error("Couldn't get balance"); // User is new
    }

    return [...this.getDeposits(obligations), ...this.getBorrows(obligations)];
  }

  async getKaminoDepositions(
    walletAddress: string,
    mintAddress: string | undefined,
  ) {
    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const obligations = await market.getObligationByWallet(
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
    );

    if (!obligations) {
      throw new Error("Couldn't get balance"); // User is new
    }

    if (mintAddress) {
      const deposit = this.getDeposit(obligations, new PublicKey(mintAddress));

      if (!deposit) {
        throw new Error("Couldn't find deposited asset");
      }

      return [deposit];
    } else {
      return this.getDeposits(obligations);
    }
  }

  async getKaminoBorrows(
    walletAddress: string,
    mintAddress: string | undefined,
  ) {
    const market = await KaminoMarket.load(
      this.connection,
      KAMINO_MAIN_MARKET_ADDRESS,
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const obligations = await market.getObligationByWallet(
      new PublicKey(walletAddress),
      new VanillaObligation(PROGRAM_ID),
    );

    if (!obligations) {
      throw new Error("Couldn't get balance"); // User is new
    }

    if (mintAddress) {
      const borrowed = this.getBorrow(obligations, new PublicKey(mintAddress));

      if (!borrowed) {
        throw new Error("Couldn't find borrowed asset");
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
