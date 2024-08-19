import mapboxgl, { Marker } from "mapbox-gl";
import React, { useEffect, useContext, useState } from "react";
import {MapContext} from '../App'
import axios from 'axios'
import style from '../../style/style.json'//for later

mapboxgl.accessToken = import.meta.env.VITE_MAPBOX_GL_API_KEY
mapboxgl.setRTLTextPlugin(
    'https://api.mapbox.com/mapbox-gl-js/plugins/mapbox-gl-rtl-text/v0.2.3/mapbox-gl-rtl-text.js',
    null,
    true // Lazy load the plugin
);//fixes arabic text

function Map() {

    const {mapRef,setMapLoaded,lng,lat,zoom} = useContext(MapContext)
    // mapRef.current will give us access to the DOM node for div, 
    // in which we will render the map and access its methods and properties

    const options = {
        container: 'mapID',
        style: 'mapbox://styles/marcas123/clyaaadm500jq01pm8eml9ud9',
        center: [lng, lat],
        zoom: zoom,
        projection: 'mercator',
        attributionControl: false,
    }

     //fetches bus stops and sets map loaded to true
  const fetchBusStops = async (map) => {
    await axios.get('/api/station',{
      headers:{
        'Content-Type': 'application/json'
      }
    })
    .then((res) => {
        const data=res.data.content
        //adds source for bus stops
        map.addSource('bus-stops',{
          type: 'geojson',
          data: data
        })
        //gives it a layer
        map.addLayer({
          id: 'bus-stops-layer',
          type: 'symbol',
          source: 'bus-stops',
          minzoom: 10,
          layout: {
            'icon-image': 'bus'
          }
        })
        setMapLoaded(true)
      }
    )
    .catch()
  }

    //this useEffect will run on render
    useEffect(() => {
        if(mapRef.current) return;
        //creates map
        const map = mapRef.current = new mapboxgl.Map(options);
        map.once("style.load",() => {
            fetchBusStops(map)
            //removes all transit labels except for airportd
            map.setFilter('transit-label', ['==', 'type', 'airport']);
        })
        const canvas = document.getElementsByClassName('mapboxgl-canvas')[0];
        const ctx = canvas.getContext('2d', { willReadFrequently: true });

        //creates red pulsating dot
        const size = 100;
        const pulsingBlueDot = {
            width: size,
            height: size,
            data: new Uint8Array(size * size * 4),
      
            onAdd: function () {
              const canvas = document.createElement('canvas');
              canvas.width = this.width;
              canvas.height = this.height;
              this.context = canvas.getContext('2d');
            },
      
            render: function () {
              const duration = 1000;
              const t = (performance.now() % duration) / duration;
      
              const radius = (size / 2) * 0.3;
              const outerRadius = (size / 2) * 0.7 * t + radius;
              const context = this.context;
      
              context.clearRect(0, 0, this.width, this.height);
              context.beginPath();
              context.arc(
                this.width / 2,
                this.height / 2,
                outerRadius,
                0,
                Math.PI * 2
              );
              context.fillStyle = `rgba(200, 194, 255, ${1 - t})`;
              context.fill();
      
              context.beginPath();
              context.arc(this.width / 2, this.height / 2, radius, 0, Math.PI * 2);
              context.fillStyle = 'rgba(64, 80 , 222, 1)';
              context.strokeStyle = 'white';
              context.lineWidth = 2 + 4 * (1 - t);
              context.fill();
              context.stroke();
      
              this.data = context.getImageData(0, 0, this.width, this.height).data;
      
              map.triggerRepaint();
      
              return true;
            }
        };
        //generates a static dot with the specified color
        const staticDot = (size,lineWidth,opacity, r1, g1, b1, r2 = 255, g2 = 255, b2 = 255) => {
            return {
                width: size,
                height: size,
                data: new Uint8Array(size * size * 4),
        
                onAdd: function () {
                    const canvas = document.createElement('canvas');
                    canvas.width = this.width;
                    canvas.height = this.height;
                    this.context = canvas.getContext('2d');
                },
        
                render: function () {
                    const radius = (size / 2) * 0.3;
                    const context = this.context;
        
                    context.clearRect(0, 0, this.width, this.height);
        
                    // Draw the shadow
                    context.shadowColor = 'rgba(0, 0, 0, 0.5)';
                    context.shadowBlur = 5;
                    context.shadowOffsetX = 0;
                    context.shadowOffsetY = 0;
        
                    context.beginPath();
                    context.arc(
                        this.width / 2,
                        this.height / 2,
                        radius + 2, // Slightly larger radius for shadow
                        0,
                        Math.PI * 2
                    );
                    context.fillStyle = 'rgba(0, 0, 0, 0.5)'; // Shadow color
                    context.fill();
        
                    // Clear the inner part where the actual dot will be drawn
                    context.shadowColor = 'rgba(0, 0, 0, 0.5)';
                    context.shadowBlur = 2;
                    context.clearRect(
                        this.width / 2 - radius - 2,
                        this.height / 2 - radius - 2,
                        (radius + 2) * 2,
                        (radius + 2) * 2
                    );
        
                    // Draw the actual dot
                    context.beginPath();
                    context.arc(
                        this.width / 2,
                        this.height / 2,
                        radius,
                        0,
                        Math.PI * 2
                    );
                    context.fillStyle = `rgba(${r1}, ${g1}, ${b1}, ${opacity})`;
                    context.fill();
        
                    context.beginPath();
                    context.arc(this.width / 2, this.height / 2, radius, 0, Math.PI * 2);
                    context.strokeStyle = `rgba(${r2}, ${g2}, ${b2}, ${opacity})`;
                    context.lineWidth = lineWidth;
                    context.stroke();
        
                    this.data = context.getImageData(0, 0, this.width, this.height).data;
        
                    map.triggerRepaint();
        
                    return true;
                }
            };
        };
        //uses addImage to add pulsingDot to the style as an icon-image called 'pulsing-dot'
        map.addImage('pulsing-blue-dot', pulsingBlueDot, { pixelRatio: 2 });
        map.addImage('static-green-dot', staticDot(100, 5, 1, 94, 199, 2), { pixelRatio: 2 })
        map.addImage('static-yellow-dot', staticDot(100, 5, 1, 237, 186, 2), { pixelRatio: 2 })
        map.addImage('static-red-dot', staticDot(100, 5, 1, 252, 99, 10), { pixelRatio: 2 })
        map.addImage('static-blue-dot', staticDot(40, 2,1 ,64 ,80 ,222))
        map.addImage('static-grey-dot', staticDot(100, 4, 0.5, 160,160,160), { pixelRatio: 2 })
        //now can use ...' as 'icon-image' of some layer
    },[]);
    return (
        <div id='mapID' className='h-full'/>
    );
}

export default Map;