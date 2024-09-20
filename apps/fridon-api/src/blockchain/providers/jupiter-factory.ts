import {
  ConfigurationParameters,
  createJupiterApiClient,
  DefaultApi,
} from '@jup-ag/api';
import { HttpException, Injectable } from '@nestjs/common';
import { Connection, PublicKey, VersionedTransaction } from '@solana/web3.js';
import {
  DONATION_ADDRESS,
  PRIORITY_FEE,
  SOL_MINT_ADDRESS,
  SWAP_FEE_BPS,
  SWAP_REFERRAL_PROGRAM_ADDRESS,
  WSOL_MINT_ADDRESS,
} from '../utils/constants';

@Injectable()
export class JupiterFactory {
  constructor(private readonly connection: Connection) {}

  private initializeJupiterClient(config: ConfigurationParameters): DefaultApi {
    return createJupiterApiClient(config);
  }

  private async quote(
    jupiter: DefaultApi,
    fromToken: string,
    toToken: string,
    amount: number,
  ) {
    try {
      const quote = await jupiter.quoteGet({
        inputMint: fromToken,
        outputMint: toToken,
        amount: amount,
        platformFeeBps: SWAP_FEE_BPS,
      });
      if (!quote) {
        throw new HttpException('Quote not found', 404);
      }

      return quote;
    } catch (e) {
      console.error('Quote Failed', e);
      throw new HttpException('Quote failed', 500);
    }
  }

  async swapTokens(
    walletAddress: string,
    fromToken: string,
    toToken: string,
    amount: number,
  ) {
    const jupiter = this.initializeJupiterClient({});

    const quote = await this.quote(jupiter, fromToken, toToken, amount);
    // todo: write checker if balance is enough.
    const inputMintAddress =
      quote.inputMint === WSOL_MINT_ADDRESS.toBase58()
        ? SOL_MINT_ADDRESS.toBase58()
        : quote.inputMint;

    inputMintAddress;

    // Fee Account
    const [feeAccount] = PublicKey.findProgramAddressSync(
      [
        Buffer.from('referral_ata'),
        DONATION_ADDRESS.toBuffer(), // your referral account public key
        new PublicKey(quote.outputMint).toBuffer(), // the token mint
      ],
      SWAP_REFERRAL_PROGRAM_ADDRESS, // the Referral Program
    );
    const accountInfo = await this.connection.getAccountInfo(feeAccount);

    try {
      const swapRes = await jupiter.swapPost({
        swapRequest: {
          userPublicKey: walletAddress,
          feeAccount: accountInfo ? feeAccount.toBase58() : undefined,
          quoteResponse: quote,
          dynamicComputeUnitLimit: true,
          prioritizationFeeLamports: PRIORITY_FEE,
        },
      });

      const txBuffer = Buffer.from(swapRes.swapTransaction, 'base64');

      return VersionedTransaction.deserialize(txBuffer);
    } catch (e) {
      console.error('Swap Failed', e);
      throw new HttpException('Swap failed', 500);
    }
  }
}
