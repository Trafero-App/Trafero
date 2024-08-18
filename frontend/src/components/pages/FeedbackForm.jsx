import { useState } from "react"
import axios from "axios"
import { useNavigate } from "react-router-dom"
import { ClipLoader } from "react-spinners"

const FeedbackForm = () => {

    const navigate = useNavigate()

    const [feedback, setFeedback] = useState('')
    const [success, setSuccess] = useState(false)
    const [isPosting, setPosting] = useState(false)

    const sendFeedback = async () => {
        await axios({
            method: 'post',
            url: '/api/app_feedback',
            headers: {
                'Content-Type': 'application/json'
            },
            data: {
                feedback: feedback
            }
        })
        .then((res) => {
            if(res.status==200){
                setSuccess(true)
                setTimeout(() => {
                    navigate('/map')
                    window.location.reload()//because navigate inside setTimeout doesnt trigger rerender
                },1000)
            }
        })
    }

    return (
        <div className="absolute h-full w-full flex flex-col md:flex-row md:justify-around items-center justify-center p-3 backdrop-blur-sm bg-black bg-opacity-10">
            <div className='bg-white w-full max-w-[30rem] rounded-xl shadow-md max-h-full p-6'>
                <h1 className='font-semibold pb-3'>Your feedback is essential to us. Please use the box below to report any issues you encounter or suggest new features or data to be added.</h1>
                <textarea
                value={feedback}
                placeholder="Enter your feedback here"
                onChange={(e) => setFeedback(e.target.value)}
                className="focus:outline-none w-full bg-gray1 placeholder:text-gray4 rounded-xl h-32 px-4 py-3"
                />
                <div className='min-h-3 w-full flex items-center'>
                    {success &&
                    <h1 className='text-xs py-1 text-blue3'>Thanks for your feedback! Redirecting you to map</h1>
                    }
                </div>
                <div className='flex justify-center items-center'>
                    <div 
                    className="py-2 flex justify-center items-center bg-blue3 rounded-xl hover:bg-blue4 transition duration-200 cursor-pointer w-44"
                    onClick={() => {
                        if(!isPosting){
                            sendFeedback()
                            setPosting(true)
                        }
                    }}
                    >
                        {isPosting ?
                        <ClipLoader size='24px' color="white"/>
                        :
                        <h1 className="text-white">Submit</h1>
                        }
                        
                    </div>
                </div>
            </div>
        </div>
    )
}

export default FeedbackForm