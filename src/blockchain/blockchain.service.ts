import { Injectable } from '@nestjs/common';
import { Connection, PublicKey } from '@solana/web3.js';
import {
  getDestinationAddress,
  getLatestBlockHash,
  getTokenSupply,
} from './utils/connection';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
import { TokenAmount } from './utils/token-amount';
import {
  KaminoAction,
  KaminoMarket,
  KaminoReserve,
  PROGRAM_ID,
  VanillaObligation,
  buildVersionedTransaction,
} from '@hubbleprotocol/kamino-lending-sdk';
import { DONATION_ADDRESS } from './utils/constants';

@Injectable()
export class BlockchainService {
  constructor(readonly connection: Connection) {}

  async getLatestsBlockHash(): Promise<string> {
    const res = await getLatestBlockHash(this.connection);
    return res.blockhash;
  }

  async createTokenAccount(): Promise<string> {
    return 'tokenAccount';
  }

  async transferTokens(
    from: string,
    to: string,
    mintAddress: string,
    amount: number,
  ): Promise<Uint8Array> {
    const tokenInfo = await getTokenSupply(mintAddress, this.connection);

    if (!tokenInfo) {
      throw new Error('Token Supply not found');
    }

    const receiver = await getDestinationAddress(this.connection, to);

    if (!receiver) {
      throw new Error('Receiver not found');
    }

    const decimals = tokenInfo.value.decimals;
    const amountBN = new TokenAmount(amount, decimals, false).toWei();

    const transferTransaction =
      await TokenProgramTransactionFactory.Instance.generateTransferTransaction(
        from,
        receiver,
        mintAddress,
        amountBN,
        this.connection,
      );

    const serializedTransaction = transferTransaction.serialize();
    console.log('transferTransaction', serializedTransaction);

    return serializedTransaction;
  }

  // Kamino Services.
  async getKaminoVaultInformation() {
    console.log('Hello, Kamino!');

    const market = await KaminoMarket.load(
      this.connection,
      new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'),
    );

    // console.log(market);

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const { reserves } = market;

    const vaults: KaminoVaultType[] = [];

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

      vaults.push({
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
      });
      console.log('Symbol: %o', symbol);
      console.log('Decimals: %o', decimals);
      console.log(
        'Reserve address: %o (https://explorer.solana.com/address/%s)',
        address.toBase58(),
        address.toBase58(),
      );
      console.log(
        'Mint address: %o (https://explorer.solana.com/address/%s)',
        mintAddress,
        mintAddress,
      );
      console.log('Loan to value: %o', loanToValuePct);
      console.log(
        'Reserve deposit limit: %o (%o)',
        reserveDepositLimit
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        reserveDepositLimit,
      );
      console.log(
        'Reserve borrow limit: %o (%o)',
        reserveBorrowLimit
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        reserveBorrowLimit,
      );
      console.log('Mint total supply: %o', mintTotalSupply.toString());
      console.log(
        'Total supply: %o (%o)',
        totalSupply
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        totalSupply,
      );
      console.log(
        'Total borrows: %o (%o)',
        totalBorrows
          .div(10 ** decimals)
          .toDecimalPlaces(decimals)
          .toString(),
        totalBorrows,
      );
      console.log('Deposit TVL (USD): %o', depositTvl);
      console.log();
    });

    return vaults;
  }

  async supplyOnKamino(
    walletAddress: string,
    mintAddress: string,
    amount: number,
  ) {
    const payer = new PublicKey(walletAddress);
    const market = await KaminoMarket.load(
      this.connection,
      new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'),
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const { reserves } = market;
    const reserveValues: KaminoReserve[] = Object.values(reserves);

    const reserve = reserveValues.find(
      (reserve) => reserve.stats.mintAddress.toBase58() === mintAddress,
    );

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

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
    ];

    const transaction = await buildVersionedTransaction(
      this.connection,
      payer,
      instructions,
    );

    return transaction;
  }

  async borrowOnKamino(
    walletAddress: string,
    mintAddress: string,
    amount: number,
  ) {
    const payer = new PublicKey(walletAddress);
    const market = await KaminoMarket.load(
      this.connection,
      new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'),
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const { reserves } = market;
    const reserveValues: KaminoReserve[] = Object.values(reserves);

    const reserve = reserveValues.find(
      (reserve) => reserve.stats.mintAddress.toBase58() === mintAddress,
    );

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

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
    ];

    const transaction = await buildVersionedTransaction(
      this.connection,
      payer,
      instructions,
    );

    return transaction;
  }

  async repayOnKamino(
    walletAddress: string,
    mintAddress: string,
    amount: number,
  ) {
    const payer = new PublicKey(walletAddress);
    const market = await KaminoMarket.load(
      this.connection,
      new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'),
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const { reserves } = market;
    const reserveValues: KaminoReserve[] = Object.values(reserves);

    const reserve = reserveValues.find(
      (reserve) => reserve.stats.mintAddress.toBase58() === mintAddress,
    );

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

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
    ];

    const transaction = await buildVersionedTransaction(
      this.connection,
      payer,
      instructions,
    );

    return transaction;
  }

  async withdrawOnKamino(
    walletAddress: string,
    mintAddress: string,
    amount: number,
  ) {
    const payer = new PublicKey(walletAddress);
    const market = await KaminoMarket.load(
      this.connection,
      new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'),
    );

    if (market == null) {
      throw new Error("Couldn't load market");
    }

    const { reserves } = market;
    const reserveValues: KaminoReserve[] = Object.values(reserves);

    const reserve = reserveValues.find(
      (reserve) => reserve.stats.mintAddress.toBase58() === mintAddress,
    );

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

    const instructions = [
      ...kaminoAction.setupIxs,
      ...kaminoAction.lendingIxs,
      ...kaminoAction.cleanupIxs,
    ];

    const transaction = await buildVersionedTransaction(
      this.connection,
      payer,
      instructions,
    );

    return transaction;
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
