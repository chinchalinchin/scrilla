import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class LogService {
  logs : string[] = [];

  constructor() { }

  public log(message: string, location: string) : void{ 
    let date = new Date();
    let formattedMessage = `${date} : ${location}: ${message}`;
    console.log(formattedMessage);
    this.logs.push(formattedMessage); 
  }

  public clear(){ this.logs = []; }
}
