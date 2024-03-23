import { Connection, PublicKey } from '@solana/web3.js';
import {
  KaminoAction,
  KaminoMarket,
  KaminoReserve,
  PROGRAM_ID,
  VanillaObligation,
  buildVersionedTransaction,
} from '@hubbleprotocol/kamino-lending-sdk';
import { TokenAmount } from '../utils/tools/token-amount';
import {
  DONATION_ADDRESS,
  KAMINO_MAIN_MARKET_ADDRESS,
} from '../utils/constants';
import { Injectable } from '@nestjs/common';
// import { Response } from '../utils/types';

// type TransactionResponseData = {
//     transaction: VersionedTransaction;
// };

@Injectable()
export class KaminoFactory {
  constructor() {}

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
      5_000_000,
      undefined,
      undefined,
      undefined,
      DONATION_ADDRESS,
    );

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
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
      5_000_000,
      true,
      false,
      true,
      DONATION_ADDRESS,
    );

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
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
      5_000_000,
      true,
      undefined,
      undefined,
      DONATION_ADDRESS,
    );

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
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
      5_000_000,
      true,
      undefined,
      undefined,
      DONATION_ADDRESS,
    );

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
    ];

    const transaction = await buildVersionedTransaction(
      connection,
      payer,
      instructions,
    );

    return transaction;
  }
}
