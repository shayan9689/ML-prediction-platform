export const REGIONS = [
  { id: "sf_bay", label: "San Francisco Bay Area", longitude: -122.42, latitude: 37.77, ocean_proximity: "NEAR BAY" },
  { id: "east_bay", label: "East Bay (Oakland / Berkeley)", longitude: -122.27, latitude: 37.8, ocean_proximity: "NEAR BAY" },
  { id: "south_bay", label: "Silicon Valley / South Bay", longitude: -121.89, latitude: 37.34, ocean_proximity: "<1H OCEAN" },
  { id: "la_coast", label: "Los Angeles coast", longitude: -118.24, latitude: 34.05, ocean_proximity: "NEAR OCEAN" },
  { id: "orange", label: "Orange County", longitude: -117.83, latitude: 33.72, ocean_proximity: "<1H OCEAN" },
  { id: "san_diego", label: "San Diego", longitude: -117.16, latitude: 32.72, ocean_proximity: "NEAR OCEAN" },
  { id: "sb", label: "Santa Barbara coast", longitude: -119.7, latitude: 34.42, ocean_proximity: "NEAR OCEAN" },
  { id: "central_valley", label: "Central Valley (Fresno / inland)", longitude: -119.79, latitude: 36.74, ocean_proximity: "INLAND" },
  { id: "sacramento", label: "Sacramento", longitude: -121.49, latitude: 38.58, ocean_proximity: "INLAND" },
];

const INTERNET_ADDONS = [
  "OnlineSecurity",
  "OnlineBackup",
  "DeviceProtection",
  "TechSupport",
  "StreamingTV",
  "StreamingMovies",
];

export const TASK_META = {
  house_price: {
    id: "house_price",
    name: "Neighborhood value",
    type: "regression",
    kicker: "Housing",
    description: "Typical home value for a California area. Pick a region — no map coordinates.",
    resultTitle: "Estimated value (USD)",
  },
  churn: {
    id: "churn",
    name: "Customer retention",
    type: "classification",
    kicker: "Telecom",
    description: "Will this customer stay or leave? Short plan details only.",
    resultTitle: "Stay or leave",
  },
  loan_default: {
    id: "loan_default",
    name: "Loan risk score",
    type: "probability",
    kicker: "Lending",
    description: "How risky is this loan application? Income, amount, and credit yes/no.",
    resultTitle: "Risk score",
  },
};

export const SCENARIOS = {
  house_price: [
    {
      id: "bay_pro",
      label: "Bay Area professional",
      values: { region: "sf_bay", annual_income: 120000, home_age: 28, rooms_per_home: 6, bedrooms_per_home: 2, households: 380 },
    },
    {
      id: "valley_family",
      label: "Central Valley family",
      values: { region: "central_valley", annual_income: 52000, home_age: 32, rooms_per_home: 5.5, bedrooms_per_home: 2, households: 450 },
    },
  ],
  churn: [
    {
      id: "flight_risk",
      label: "New fiber, month-to-month",
      values: {
        gender: "Female",
        SeniorCitizen: "No",
        Partner: "No",
        Dependents: "No",
        tenure: 2,
        PhoneService: "Yes",
        InternetService: "Fiber optic",
        OnlineSecurity: "No",
        OnlineBackup: "No",
        DeviceProtection: "No",
        TechSupport: "No",
        Streaming: "Yes",
        Contract: "Month-to-month",
        PaperlessBilling: "Yes",
        PaymentMethod: "Electronic check",
        MonthlyCharges: 94.5,
      },
    },
    {
      id: "loyal",
      label: "Two-year loyal customer",
      values: {
        gender: "Male",
        SeniorCitizen: "No",
        Partner: "Yes",
        Dependents: "Yes",
        tenure: 58,
        PhoneService: "Yes",
        InternetService: "DSL",
        OnlineSecurity: "Yes",
        OnlineBackup: "Yes",
        DeviceProtection: "Yes",
        TechSupport: "Yes",
        Streaming: "No",
        Contract: "Two year",
        PaperlessBilling: "No",
        PaymentMethod: "Credit card (automatic)",
        MonthlyCharges: 64.2,
      },
    },
  ],
  loan_default: [
    {
      id: "strong",
      label: "Graduate, clean credit",
      values: {
        Gender: "Male",
        Married: "Yes",
        Dependents: "1",
        Education: "Graduate",
        Self_Employed: "No",
        ApplicantIncome: 5800,
        CoapplicantIncome: 1500,
        LoanAmount: 128,
        Loan_Amount_Term: 360,
        Credit_History: "Yes",
        Property_Area: "Semiurban",
      },
    },
    {
      id: "thin_file",
      label: "No credit history",
      values: {
        Gender: "Female",
        Married: "No",
        Dependents: "0",
        Education: "Not Graduate",
        Self_Employed: "Yes",
        ApplicantIncome: 2800,
        CoapplicantIncome: 0,
        LoanAmount: 110,
        Loan_Amount_Term: 180,
        Credit_History: "No",
        Property_Area: "Rural",
      },
    },
  ],
};

export function defaultForm(taskId) {
  if (taskId === "house_price") {
    return { region: "sf_bay", annual_income: 75000, home_age: 30, rooms_per_home: 5.5, bedrooms_per_home: 1.1, households: 400 };
  }
  if (taskId === "churn") {
    return { ...SCENARIOS.churn[0].values };
  }
  return { ...SCENARIOS.loan_default[0].values };
}

export function visibleGroups(taskId, form) {
  if (taskId === "house_price") {
    return [
      {
        title: "Location",
        note: "We map the region to California coordinates internally. You never enter latitude or longitude.",
        fields: [
          {
            name: "region",
            label: "California region",
            type: "select",
            options: REGIONS.map((r) => ({ value: r.id, label: r.label })),
          },
        ],
      },
      {
        title: "Neighborhood profile",
        note: "Think of a typical block, not one street address.",
        fields: [
          {
            name: "annual_income",
            label: "Typical household income",
            type: "currency",
            suffix: "/ year",
            help: "Gross yearly income for a typical household in this neighborhood.",
          },
          { name: "home_age", label: "Typical home age", type: "number", suffix: "years" },
          {
            name: "households",
            label: "Households in the area",
            type: "number",
            suffix: "homes",
            help: "Census-block size. 300–500 homes is common.",
          },
          { name: "rooms_per_home", label: "Rooms per home", type: "number", step: "0.1", suffix: "rooms" },
          { name: "bedrooms_per_home", label: "Bedrooms per home", type: "number", step: "0.1", suffix: "bedrooms" },
        ],
      },
    ];
  }

  if (taskId === "churn") {
    const hasPhone = form.PhoneService !== "No";
    const hasNet = form.InternetService && form.InternetService !== "No";
    const groups = [
      {
        title: "Customer",
        fields: [
          { name: "gender", label: "Gender", type: "select", options: ["Female", "Male"] },
          { name: "SeniorCitizen", label: "Senior citizen", type: "select", options: ["No", "Yes"] },
          { name: "Partner", label: "Has a partner", type: "select", options: ["Yes", "No"] },
          { name: "Dependents", label: "Has dependents", type: "select", options: ["Yes", "No"] },
        ],
      },
      {
        title: "Plan",
        fields: [
          { name: "tenure", label: "Time with the company", type: "number", suffix: "months" },
          { name: "Contract", label: "Contract", type: "select", options: ["Month-to-month", "One year", "Two year"] },
          { name: "PhoneService", label: "Phone service", type: "select", options: ["Yes", "No"] },
          { name: "InternetService", label: "Internet", type: "select", options: ["DSL", "Fiber optic", "No"] },
          { name: "MonthlyCharges", label: "Monthly charges", type: "currency", suffix: "/ month" },
        ],
      },
    ];
    if (hasNet) {
      groups.push({
        title: "Add-ons",
        note: "Hidden when internet is off — that was a common bug in the old form.",
        fields: [
          { name: "OnlineSecurity", label: "Online security", type: "select", options: ["No", "Yes"] },
          { name: "OnlineBackup", label: "Online backup", type: "select", options: ["No", "Yes"] },
          { name: "DeviceProtection", label: "Device protection", type: "select", options: ["No", "Yes"] },
          { name: "TechSupport", label: "Tech support", type: "select", options: ["No", "Yes"] },
          { name: "Streaming", label: "Streaming TV & movies", type: "select", options: ["No", "Yes"] },
        ],
      });
    }
    groups.push({
      title: "Billing",
      fields: [
        { name: "PaperlessBilling", label: "Paperless billing", type: "select", options: ["Yes", "No"] },
        {
          name: "PaymentMethod",
          label: "Payment method",
          type: "select",
          options: [
            { value: "Electronic check", label: "Electronic check" },
            { value: "Mailed check", label: "Mailed check" },
            { value: "Bank transfer (automatic)", label: "Auto bank transfer" },
            { value: "Credit card (automatic)", label: "Auto credit card" },
          ],
        },
      ],
    });
    if (!hasPhone) {
      groups[1].fields = groups[1].fields.filter((f) => f.name !== "unused");
    }
    return groups;
  }

  return [
    {
      title: "Applicant",
      fields: [
        { name: "Gender", label: "Gender", type: "select", options: ["Male", "Female"] },
        { name: "Married", label: "Married", type: "select", options: ["Yes", "No"] },
        { name: "Dependents", label: "Dependents", type: "select", options: ["0", "1", "2", "3+"] },
        { name: "Education", label: "Education", type: "select", options: ["Graduate", "Not Graduate"] },
        { name: "Self_Employed", label: "Self-employed", type: "select", options: ["Yes", "No"] },
      ],
    },
    {
      title: "Loan",
      fields: [
        { name: "ApplicantIncome", label: "Applicant income", type: "currency", suffix: "/ month" },
        { name: "CoapplicantIncome", label: "Co-applicant income", type: "currency", suffix: "/ month" },
        {
          name: "LoanAmount",
          label: "Loan amount",
          type: "number",
          suffix: "× $1,000",
          help: "Enter thousands of USD. 128 means $128,000.",
        },
        {
          name: "Loan_Amount_Term",
          label: "Term",
          type: "select",
          options: [
            { value: 120, label: "10 years" },
            { value: 180, label: "15 years" },
            { value: 240, label: "20 years" },
            { value: 300, label: "25 years" },
            { value: 360, label: "30 years" },
            { value: 480, label: "40 years" },
          ],
        },
        { name: "Credit_History", label: "Meets credit guidelines", type: "select", options: ["Yes", "No"], help: "Yes = prior credit history is in good standing." },
        { name: "Property_Area", label: "Property area", type: "select", options: ["Urban", "Semiurban", "Rural"] },
      ],
    },
  ];
}

function optValue(opt) {
  return typeof opt === "object" ? opt.value : opt;
}

export function toModelPayload(taskId, form) {
  if (taskId === "house_price") {
    const region = REGIONS.find((r) => r.id === form.region) || REGIONS[0];
    const households = Number(form.households) || 400;
    const rooms = Number(form.rooms_per_home) || 5;
    const beds = Number(form.bedrooms_per_home) || 1;
    return {
      longitude: region.longitude,
      latitude: region.latitude,
      ocean_proximity: region.ocean_proximity,
      housing_median_age: Number(form.home_age),
      households,
      population: Math.round(households * 2.8),
      total_rooms: Math.round(rooms * households),
      total_bedrooms: Math.round(beds * households),
      median_income: Number(form.annual_income) / 10000,
    };
  }

  if (taskId === "churn") {
    const hasPhone = form.PhoneService !== "No";
    const hasNet = form.InternetService !== "No";
    const streaming = form.Streaming === "Yes" ? "Yes" : "No";
    const payload = {
      gender: form.gender,
      SeniorCitizen: form.SeniorCitizen === "Yes" ? 1 : 0,
      Partner: form.Partner,
      Dependents: form.Dependents,
      tenure: Number(form.tenure),
      PhoneService: form.PhoneService,
      MultipleLines: hasPhone ? "No" : "No phone service",
      InternetService: form.InternetService,
      Contract: form.Contract,
      PaperlessBilling: form.PaperlessBilling,
      PaymentMethod: form.PaymentMethod,
      MonthlyCharges: Number(form.MonthlyCharges),
      TotalCharges: Number(form.tenure) * Number(form.MonthlyCharges),
    };
    for (const key of INTERNET_ADDONS) {
      if (!hasNet) payload[key] = "No internet service";
      else if (key === "StreamingTV" || key === "StreamingMovies") payload[key] = streaming;
      else payload[key] = form[key] === "Yes" ? "Yes" : "No";
    }
    return payload;
  }

  return {
    Gender: form.Gender,
    Married: form.Married,
    Dependents: String(form.Dependents),
    Education: form.Education,
    Self_Employed: form.Self_Employed,
    ApplicantIncome: Number(form.ApplicantIncome),
    CoapplicantIncome: Number(form.CoapplicantIncome),
    LoanAmount: Number(form.LoanAmount),
    Loan_Amount_Term: Number(form.Loan_Amount_Term),
    Credit_History: form.Credit_History === "Yes" || form.Credit_History === 1 || form.Credit_History === "1" ? 1 : 0,
    Property_Area: form.Property_Area,
  };
}

export { optValue };
