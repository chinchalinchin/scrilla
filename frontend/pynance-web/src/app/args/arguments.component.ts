import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormGroup, FormControl } from '@angular/forms';

/** ArgumentsComponent
 * Description: 
 * This component is used to parse user input and send it back to the parent 
 *  component in which it is placed. 
 * 
 * Input:
 * The ArgumentsComponent has four tags that must be specified as arguments when laying down 
 *  an instance of this component,
 * 
 *  <app-args [tickers]="true" [dates]="true" [target]="true" [model]="true"></app-args>
 * 
 * If these arguments are not provided, they default to false. These arguments configure
 *  which widgets are displayed in the component. If 'tickers' is specified, a text area will
 *  allow users to enter a list of ticker symbols separated by a comma. If 'dates' is specified,
 *  a date picker toggle will allow users to select a start date and end date. If 'target' is
 *  specified a number input field will allow users to enter a decimal. If 'model' is specified,
 *  a drop-down menu will be displayed which will allow users to select from the available pricing
 *  models (Discount Dividend Model, Discount Cashflow Model, etc.)
 * 
 * Output:
 * The ArgumentsComponent has four output events into which the parent component can wire in 
 *  functions,
 * 
 * <app-args (addTickers)="doThis($event)" (addDates)="doThat($event)" 
 *           (addTarget)="doSomething($event)" (addModel)="doAnything($event)"></app-args>
 * 
 * The 'addTickers' event will contain a string array of ticker symbol list inputted by the user. 
 *  Note, duplicate ticker symbols may exist in this list, so the parent component will have to 
 *  validate the list on its own. 
 * 
 * The 'addDates' event will contain
 *  add
 **  */
@Component({
  selector: 'app-args',
  templateUrl: './arguments.component.html'
})
export class ArgumentsComponent implements OnInit {
  // Input: Displayed argument subcomponents
  @Input()
  private tickers : boolean = false;
  @Input()
  private dates : boolean = false;
  @Input()
  private target : boolean = false;
  @Input()
  private model: boolean = false;

  // Output: User entered argument values
  @Output()
  private addTickers = new EventEmitter<string[]>();
  @Output()
  private addDates = new EventEmitter<Date[]>();
  @Output()
  private addTarget = new EventEmitter<Number>();
  @Output()
  private addModel = new EventEmitter<string>();
  
  public inputTickers: string;
  public range = new FormGroup({
    start: new FormControl(),
    end: new FormControl()
  });


  private savedTickers : string[] = [];
  private savedStartDate : Date;
  private savedEndDate : Date;
  private today : Date;

  constructor() { }

  ngOnInit() {
    this.today = new Date();
  }

  public saveTickers(){
    let parsedTickers : string[] = this.inputTickers.replace(/\s/g, "").toUpperCase().split(',');
    for(let ticker of parsedTickers){ this.savedTickers.push(ticker); }
    this.addTickers.emit(this.savedTickers);
    this.inputTickers = null;
  }
  
  public saveStartDate(date : Date) : void {
    this.savedStartDate = date;
    console.log(`savedStart (y-m-d): ${this.savedStartDate.getUTCFullYear()}-${this.savedStartDate.getUTCMonth()}-${this.savedStartDate.getDay()}`)
    console.log(`savedStart.toDateString ${this.savedStartDate.toDateString()}`)
    console.log(`savedStart.to ${this.savedStartDate.toLocaleDateString()}`)
  }

  public saveEndDate(date : Date) : void {
    this.savedEndDate = date;
    console.log(date)
  }

  public saveTargetReturn(return_rate : number) : void {
    console.log(return_rate)
  }

  public saveModel(model : string): void{
    console.log(model)
  }
}
