import { Component, EventEmitter, OnInit, Output } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';

// A component used to retrieve ticker symbols for app calculations.
// TODO: needs to emit the tickers being added.
@Component({
  selector: 'app-ticker',
  templateUrl: './ticker.component.html'
})
export class TickerComponent implements OnInit {
  public range = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });

  @Output()
  private addTickers = new EventEmitter<string[]>();
  
  public inputTickers: string;
  private tickers : string[] = [];

  constructor() { }

  ngOnInit() {
  }

  public saveTickers(){
    let parsedTickers : string[] = this.inputTickers.replace(/\s/g, "").toUpperCase().split(',');
    for(let ticker of parsedTickers){ this.tickers.push(ticker); }
    this.addTickers.emit(this.tickers);
    this.inputTickers = null;
  }
  
  public setStartDate(date : Date) : void {
    console.log(date)
  }

  public setEndDate(date : Date) : void {
    console.log(date)
  }
}
