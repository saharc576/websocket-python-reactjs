import TableComp from "./TableComp";
import React, { Component } from "react";
 import { w3cwebsocket as W3CWebSocket } from "websocket";

 const client = new W3CWebSocket('ws://localhost:8765');
 const sports = ["soccer", "tennis", "table tennis", "volleyball", "basketball"]

 function App() {

     const [data, setData] = React.useState("never started")
     const [sportName, setSportName] = React.useState("")
      React.useEffect(
        () => {
          client.onopen = () => {
            console.log('WebSocket Client Connected');
          };
          client.onmessage = (message) => {
            setData(JSON.parse(message.data))
          };
        }, []
      )
         const refreshDataHandler = () => {
            client.send("refresh data@basketball")
             console.log("client requested from server to refresh data")
         }

         const changeToDifferentSport = (sportName) => {
            client.send("change to@" + sportName)
             setSportName(sportName)
             console.log("client requested from server to change sport")
         }

     return (
         <div>
             <div>
                     {sports.map((name, i) => {
                        return (
                            <button onClick={() => changeToDifferentSport(name)}>change to {name}</button>
                        )
                    })
                 }

             </div>
             <div>
                 <button onClick={refreshDataHandler}>
                     Refresh Data For Current Sport
                 </button>
             </div>
             {sportName !== "" && <h3 style={{"textAlign": "center"}}>{sportName.toLocaleUpperCase()}</h3>}
             {(data === "never started" ) ?
                 (<h1>Please choose sport from the above buttons</h1>) :
                 (data.matches === undefined) ? (
                <p>Loading ...</p>
             ): (
                 <TableComp matchesList={data.matches}/>
                 )
             }
         </div>
     );
}
// let sports = [soccer, tennis, tableTennis, volleyball, basketball]
// let colors = ["lightblue", "beige", "lightgrey", "snow", "beige"]
// class App extends Component {
//   constructor() {
//     super({counter : 0});
//   }
//
//
//   render() {
//     return (
//       <div>
//           {sports.map((sport, key) => {
//             return (
//                 <div style={{"backgroundColor": colors[key]}}>
//                     {sport.countries.map((country, key) => {
//                         return (
//                           <div>
//                             {country.leagues.map((league, key) => {
//                               return (
//                                 <div>
//                                   <TableComp matchesList={league.matches} tableName={sport.name +  " " + country.name + " " + league.name}/>
//                                 </div>
//
//                               )
//                             })}
//                           </div>
//
//                         );
//                       })
//                     }
//
//                 </div>
//
//             )
//           })}
//       </div>
//     )
//   }
// }
export default App;
