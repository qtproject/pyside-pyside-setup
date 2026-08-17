// @snippet capture-maximumframerate
Returns the capture frame rate upper limit.
// @snippet capture-maximumframerate

// @snippet capture-setmaximumframerate
Sets the capture frame rate upper limit. This can be set to override the
capture frame rate used by default based on e.g. display refresh rate, but only
as an upper limit since the class produces frames at a variable rate.
Setting this higher than the display refresh rate is not recommended and can
cause errors. Any changes to this property are applied the next time the
class goes active.
// @snippet capture-setmaximumframerate
