import { Component, ɵCodegenComponentFactoryResolver } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html'
})
export class AppComponent {
  public title : string = 'pynance-web';
  public explanations : boolean = false;
}
