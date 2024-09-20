import {
  OnGatewayConnection,
  WebSocketGateway,
  WebSocketServer,
  WsException,
} from '@nestjs/websockets';
import { Injectable } from '@nestjs/common';
import { Socket, Server } from 'socket.io';

@WebSocketGateway({ cors: { origin: '*' } })
@Injectable()
export class EventsGateway implements OnGatewayConnection {
  @WebSocketServer()
  private readonly server: Server;

  async handleConnection(client: Socket) {
    try {
      const { walletId } = this.getClientInfoFromAuth(client);

      await client.join(walletId);
    } catch (e) {
      setTimeout(() => {
        client._error('Unauthorized');
        client.disconnect();
      }, 1000);
    }
  }

  public sendTo(walletId: string, event: string, data: any) {
    this.server.to(walletId).emit(event, data);
  }

  private getClientInfoFromAuth(socket: Socket): { walletId: string } {
    const walletId = socket.handshake.query['walletId'];

    if (!walletId) throw new WsException('Unauthorized');
    if (typeof walletId !== 'string') throw new WsException('Unauthorized');

    return { walletId: walletId };
  }
}
