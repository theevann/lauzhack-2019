import React from 'react';
import { useRef, useState, useEffect } from 'react';
import { Container, Spinner, Button } from 'react-bootstrap';
import { Row } from 'react-bootstrap';
import { Col } from 'react-bootstrap';
import $ from 'jquery'


const FOOD_CAM = 'c922'
const PERSON_CAM = 'Integrated'


const HomePage = () => {
  const foodRef = useRef(null);
  const personRef = useRef(null);

  const [transaction, setTransaction] = useState(null)

  navigator.mediaDevices.enumerateDevices().then(devices => {

    var promises = devices.filter(device => device.kind == "videoinput").map(camera => {
      navigator.mediaDevices.getUserMedia({
        video: {
          deviceId: { exact: camera.deviceId },
          width: 440,
          height: 440
        }
      }).then(stream => {
        if (camera.label.startsWith(FOOD_CAM)) {
          (foodRef.current).srcObject = stream;
        }
        if (camera.label.startsWith(PERSON_CAM) && personRef.current) {
          (personRef.current).srcObject = stream;
          (foodRef.current).srcObject = stream;
        }
      })
    });
  })



  const screenshot = (video) => {
    let w = video.videoWidth;
    let h = video.videoHeight;
    let canvas = document.createElement('canvas');
    canvas.width = w;
    canvas.height = h;
    let ctx = canvas.getContext('2d');
    if (ctx) {
      ctx.drawImage(video, 0, 0, w, h);
      return canvas.toDataURL('image/jpeg');
    }
  }

  const takeScreenshot = () => {
    let screenshots = {
      person: screenshot(personRef.current),
      food: screenshot(foodRef.current)
    };

    $.ajax({
      url: 'http://localhost:5000/dish',
      type: "post",
      data: JSON.stringify(screenshots),
      headers: {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': "*"
      },
      success: function (data) {
        if (data.food !== "empty") {
          setTransaction(data);
        }
      }
    });

    // fetch('http://localhost:5000/dish', {
    //   method: 'POST',
    //   mode: 'no-cors', // no-cors, *cors, same-origin
    //   // cache: 'no-cache', // *default, no-cache, reload, force-cache, only-if-cached
    //   // credentials: 'same-origin', // include, *same-origin, omit
    //   headers: {
    //     'Content-Type': 'application/json'
    //   },
    //   body: JSON.stringify(screenshots)
    // }).then((response) => {
    //   response.json().then((data) => {
    //     console.log(data);
    //     if (data.food !== "background") {
    //       setTransaction(data)
    //     }
    //   })
    // })
  }

  const reset = () => {
    setTransaction(null);
  };

  useEffect(() => {
    let interval = null;
    if (!transaction) {
      interval = setInterval(() => {
        takeScreenshot();
      }, 3000);
    } else {
      clearInterval(interval);
    }
    return () => clearInterval(interval);
  }, [transaction]);

  return (
    <Container>
      <h1 className="mt-5">
        Checkout
        </h1>
      <Row className="mt-4">
        <Col sm={8}>
          <video ref={foodRef} autoPlay playsInline muted style={{ 'width': '100%' }} />
          {transaction && (
            <h2 className="text-center">
              {transaction.food} - ${transaction.price}
            </h2>
          )}
          {!transaction && (
            <h2 className="text-center">
              Food:
              <Spinner animation="grow" />
              <Spinner animation="grow" />
              <Spinner animation="grow" />
            </h2>
          )}
        </Col>

        <Col sm={4}>
          <video ref={personRef} autoPlay playsInline muted style={{ 'width': '100%' }} />
          {transaction && (
            <h1>{transaction.person}<br /><small>{transaction.status}</small></h1>
          )}
          {!transaction && (
            <div className="text-center">
              <Spinner animation="grow" />
              <Spinner animation="grow" />
              <Spinner animation="grow" />
            </div>
          )}
          <Button variant="primary" onClick={takeScreenshot}>Screenshot</Button>
          <Button className="ml-2" variant="primary" onClick={reset}>Reset</Button>
        </Col>
      </Row>
    </Container >
  )
};

export default HomePage;
