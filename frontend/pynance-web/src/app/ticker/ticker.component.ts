import { Component, EventEmitter, OnInit, Output } from '@angular/core';

// A component used to retrieve ticker symbols for app calculations.
// TODO: needs to emit the tickers being added.
@Component({
  selector: 'app-ticker',
  templateUrl: './ticker.component.html'
})
export class TickerComponent implements OnInit {

  @Output()
  private addTickers = new EventEmitter<string[]>();
  
  private tickers : string[];

  constructor() { }

  ngOnInit() {
  }

  public saveTickers(tickerList: string[]){
    for(let ticker in tickerList){ 
      // TODO: check if ticker is already in this.tickers
      this.tickers.push(ticker)
    }
  }
  public emitTickers(){
    this.addTickers.emit(this.tickers);
  }
}
