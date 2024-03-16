import { Injectable } from '@nestjs/common';
import { Connection } from '@solana/web3.js';
import { getLatestBlockHash } from './utils/connection';
import { TokenProgramTransactionFactory } from './factories/token-program-transaction-factory';
// import { KaminoMarket } from '@hubbleprotocol/kamino-lending-sdk';
import { PublicKey } from '@metaplex-foundation/js';

@Injectable()
export class BlockchainService {
  constructor(readonly connection: Connection) {}

  async getLatestsBlockHash(): Promise<string> {
    const res = await getLatestBlockHash();
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
  ): Promise<boolean> {
    const transactionMessage =
      await TokenProgramTransactionFactory.Instance.generateTransferTransaction(
        from,
        to,
        mintAddress,
        amount,
        this.connection,
      );

    console.log('transactionMessage', transactionMessage);

    return true;
  }

  // async getKaminoVaultInformation() {
  //   console.log('Hello, Kamino!');

  //   const market = await KaminoMarket.load(
  //     this.connection,
  //     new PublicKey('7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF'), // main market address. Defaults to 'Main' market
  //   );

  //   console.log(market);

  //   if (market == null) {
  //     throw new Error("Couldn't load market");
  //   }

  //   const { reserves } = market;

  //   const info = Object.values(reserves).map((reserve) => {
  //     const {
  //       symbol,
  //       address,
  //       stats: {
  //         decimals,
  //         mintAddress,
  //         loanToValuePct,
  //         reserveDepositLimit,
  //         reserveBorrowLimit,
  //         mintTotalSupply,
  //       },
  //     } = reserve;
  //     const totalSupply = reserve.getTotalSupply();
  //     const totalBorrows = reserve.getBorrowedAmount();
  //     const depositTvl = reserve.getDepositTvl();

  //     return {
  //       symbol,
  //       address: address.toBase58(),
  //       decimals,
  //       mintAddress,
  //       loanToValuePct,
  //       reserveDepositLimit: reserveDepositLimit
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       reserveBorrowLimit: reserveBorrowLimit
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       mintTotalSupply: mintTotalSupply.toString(),
  //       totalSupply: totalSupply
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       totalBorrows: totalBorrows
  //         .div(10 ** decimals)
  //         .toDecimalPlaces(decimals)
  //         .toString(),
  //       depositTvl,
  //     } as KaminoVaultType;
  //   });

  //   return info;
  // }
}

export type KaminoVaultType = {
  symbol: string;
  address: string;
  decimals: number;
  mintAddress: string;
  loanToValuePct: number;
  reserveDepositLimit: number;
  reserveBorrowLimit: number;
  mintTotalSupply: number;
  totalSupply: number;
  totalBorrows: number;
  depositTvl: number;
};
