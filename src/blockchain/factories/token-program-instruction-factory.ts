import { Connection, PublicKey, PublicKeyInitData, TransactionInstruction, } from "@solana/web3.js";
import { createAssociatedTokenAccountInstruction, createTransferInstruction } from "@solanal/spl-token";
import { findAssociatedTokenAddress } from "../utils/connection";



export class TokenProgramInstructionFactory {
    private static _instance: TokenProgramInstructionFactory;

    public static get Instance(): TokenProgramInstructionFactory {
        return this._instance || (this._instance = new this());
    }

    async createTransferInstructions(
        from: PublicKeyInitData,
        to: PublicKeyInitData,
        mintAddress: string,
        amount: number,
    ) {
        // 1) Check mintAddress associated accout.
        const source = await findAssociatedTokenAddress(from, mintAddress);
        const dest = await findAssociatedTokenAddress(to, mintAddress);


        const instruction = createTransferInstruction(
            new PublicKey(source),
            new PublicKey(dest),
            new PublicKey(from),
            amount,
        );

        return instruction;
    }

    async generateAssociatedTokenAccountInstructionsIfNeeded(
        mintAddress: PublicKeyInitData,
        to: PublicKeyInitData,
        payer: PublicKeyInitData,
        connection: Connection,
    ): Promise<TransactionInstruction | undefined> {

        // Associated token address
        const associatedTokenAddress = await findAssociatedTokenAddress(to, mintAddress);

        // get account info to check if he really needs to create token account.
        const accountInfo = await connection.getAccountInfo(associatedTokenAddress, 'confirmed');

        if (accountInfo) return undefined;

        // Create one
        const createAccountInstructions = createAssociatedTokenAccountInstruction(
            new PublicKey(payer),
            new PublicKey(associatedTokenAddress),
            new PublicKey(to),
            new PublicKey(mintAddress),
        );

        return createAccountInstructions;
    }
}